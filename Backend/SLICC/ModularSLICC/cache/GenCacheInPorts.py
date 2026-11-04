#  Copyright (c) 2022.  Nicolai Oswald
#  Copyright (c) 2022.  University of Edinburgh
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met: redistributions of source code must retain the above copyright
#  notice, this list of conditions and the following disclaimer;
#  redistributions in binary form must reproduce the above copyright
#  notice, this list of conditions and the following disclaimer in the
#  documentation and/or other materials provided with the distribution;
#  neither the name of the copyright holders nor the names of its
#  contributors may be used to endorse or promote products derived from
#  this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#
#
#

from typing import Dict, Tuple
from collections import OrderedDict

from DataObjects.ClassCluster import Cluster
from DataObjects.ClassMultiDict import MultiDict
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from Backend.SLICC.ModularSLICC.common.GenMachineInPorts import GenMachineInPorts
from Backend.SLICC.ModularSLICC.common import Util
from Backend.SLICC.ModularSLICC.common.GenPCCToSLICC import GenPCCToSLICC
from Backend.SLICC.ModularSLICC.common.GenSLICCTree import GenSLICCTree
import re


class GenCacheInPorts(TemplateHandler):

    def __init__(self, handler_dir: str):
        TemplateHandler.__init__(self, handler_dir)
        self.all_message_names = set()

    def gen_cache_in_ports_str(
            self,
            cluster: Cluster,
            arch: FlatArchitecture,
            in_ports: 'OrderedDict[str, str]',
            out_ports: 'OrderedDict[str, str]',
            machine_mappings: dict[str, str],
    ) -> str:

        return "//" + __name__ + self.nl \
               + GenMachineInPorts.gen_machine_in_ports(
                    self, cluster, arch, True, "Cache", in_ports, out_ports, machine_mappings) \
               + self.nl + self._gen_mandatory_in_port(cluster, arch, out_ports, machine_mappings) + self.nl

    def _gen_mandatory_in_port(self, cluster: Cluster, arch: FlatArchitecture, out_ports: 'OrderedDict[str, str]', machine_mappings: dict[str, str]) -> str:

        rc_accesses = Util.rc_accesses(arch)
        access_transitions = {access: MultiDict() for access in ["load", "store", "evict", "ifetch"] + rc_accesses}
        for state in sorted(arch.get_architecture_states_verified(), key=str):
            for trans in state.getaccessmiss():
                access = Util.transition_access(trans)
                assert (True, str(state)) not in access_transitions[access], \
                    f"Cannot both hit and miss the same access in the same state ({access},{str(state)})."
                access_transitions[access][(False, str(state))] = trans
            for trans in state.getaccesshit():
                access = Util.transition_access(trans)
                assert (False, str(state)) not in access_transitions[access], \
                    f"Cannot both hit and miss the same access in the same state ({access},{str(state)})."
                access_transitions[access][(True, str(state))] = trans
            evicts = list(set(state.getevict()))
            if evicts:
                assert len(evicts) == 1, f"{evicts}"
                access_transitions['evict'][(False, str(state))] = evicts[0]
                # Note we treat all evicts like "misses" as they do not require a callback to the sequencer

        load_str = self._gen_access_str(cluster, arch, access_transitions, out_ports, machine_mappings, 5, "load")
        if len(access_transitions["ifetch"]) > 0:
            # Instruction fetches have their own transitions and live in cache_instruction
            ifetch_str = self._gen_access_str(
                cluster, arch, access_transitions, out_ports, machine_mappings, 5, "ifetch")
            icache_victim = " && in_msg.Type == RubyRequestType:IFETCH"
            dcache_victim = " && in_msg.Type != RubyRequestType:IFETCH"
        else:
            # The protocol has no ifetch access, but gem5 still issues instruction fetches:
            # serve them as loads, from the data cache (cache_instruction stays unused).
            ifetch_str = load_str
            icache_victim = " && false"
            dcache_victim = ""

        template = self.open_template("mandatory_cpu_in_port.sm")
        rc_strs = []
        uncached = Util.uncached_direct_accesses(arch)
        invalid_states = {str(state) for state in Util.get_invalid_states(arch)}
        for idx, access in enumerate(rc_accesses):
            template, dispatched = self._rc_dispatch(template, access, 6 + idx)
            rc_strs.append(self._gen_access_str(
                cluster, arch, access_transitions, out_ports, machine_mappings, 5, access))
            # Served without a copy where the block is not present: no victim to make room for it
            if dispatched and all((access, state) in uncached for state in invalid_states
                                  if any((hit, state) in access_transitions[access] for hit in (True, False))):
                dcache_victim += "".join(f" && in_msg.Type != RubyRequestType:{req_type}"
                                         for req_type in Util.RC_ACCESSES[access][1])

        return self.string_repl_keys(template,
                                     [self._gen_access_str(
                                         cluster, arch, access_transitions, out_ports, machine_mappings, 4, "evict"),
                                      load_str,
                                      ifetch_str,
                                      self._gen_access_str(
                                         cluster, arch, access_transitions, out_ports, machine_mappings, 5, "store"),
                                      icache_victim,
                                      dcache_victim,
                                      ] + rc_strs
                                     )

    @staticmethod
    def _rc_dispatch(template: str, access: str, key: int) -> Tuple[str, bool]:
        """The request types of an access of release-consistency code leave the loads or the
        stores and get their own branch (gem5 v20: only alloy-gem5's DOSequencer issues them)."""
        types = Util.RC_ACCESSES[access][1]
        found = False
        for req_type in types:
            for pattern in (r"\s*\|\|\s*in_msg\.Type == RubyRequestType:" + req_type + r"\b",
                            r"in_msg\.Type == RubyRequestType:" + req_type + r"\s*\|\|\s*"):
                template, n = re.subn(pattern, "", template, count=1)
                found = found or n > 0
        if not found:
            return template, False  # the sequencer of this gem5 does not issue them
        cond = " || ".join(f"in_msg.Type == RubyRequestType:{req_type}" for req_type in types)
        last = "        } else {\n          error(\"Unexpected message type from processor\");"
        assert last in template, "mandatory_cpu_in_port.sm changed"
        return template.replace(last, f"        }} else if ({cond}) {{\n        ${key}$\n" + last, 1), True

    def _gen_access_str(
            self,
            cluster: Cluster,
            arch: FlatArchitecture,
            transition_map: Dict[str, 'MultiDict'],
            out_ports: 'OrderedDict[str, str]',
            machine_mappings: dict[str, str],
            indent_level: int,
            access_type: str
    ) -> str:

        transition_map = transition_map[access_type]  # Other accesses handled separately

        transitions_strs = []
        hit_event_map = Util.get_local_hit_events(arch)
        invalid_states = {str(state) for state in Util.get_invalid_states(arch)}
        direct_events = Util.get_direct_access_events(arch)

        for (is_hit, state_name), transitions in transition_map.items():

            slicc_tree_gen = GenSLICCTree(cluster, arch, True, "mandatory_in", out_ports,
                                          machine_mappings, allow_port_popping=False, set_final_state=(not is_hit))

            op_str = ""
            entry_alloced = False
            direct = direct_events.get((access_type, state_name)) if not is_hit else None

            if direct is not None:
                # Sent on without waiting for a reply: the access completes in its own transition
                op_str += f"trigger(Event:{direct[1]}, LineAddress, getEntry(LineAddress), tbe){self.end}"
            elif state_name in invalid_states and access_type != "evict":
                # If we are currently in an invalid state,
                # that is a state in which the line is not present in the cache,
                # we need to trigger an event which allocates the cache entry
                # before performing any operations.
                # Due to possible circular happens-before dependencies in the generated SLICC file,
                # this event also needs to handle e.g. the state transition and every operation
                # which we want to carry out at this point (e.g. setting auxiliary state).
                # Note that the transition needs to update the state using the transition syntax
                # transition(old_state, event, new_state) rather than using setState;
                # otherwise the state update will be overwritten and effectively void.
                entry_alloced = True
                next_state = str(transitions[0].final_state)
                # Assert all the transitions have the same end state, otherwise I don't know what to do...
                assert all(str(trans.final_state) == next_state for trans in transitions)
                op_str += f"trigger(Event:alloc{next_state}, LineAddress, getEntry(LineAddress), " \
                          f"tbe){self.end}"
            elif not (is_hit and Util.is_rc_store(access_type)):
                # (a hit of a store of release-consistency code writes its bytes in local_ntstoreHit)
                op_str += slicc_tree_gen.gen_slicc_tree(transitions)

            if direct is not None:
                op_str += f"{self.nl}{Util.gen_progress_str(self, True)}"
            elif is_hit:
                assert not entry_alloced, "Can't both alloc entry and hit locally"
                _, event_name = hit_event_map[(access_type, state_name)]
                op_str += f"{self.nl}trigger(Event:{event_name}, LineAddress, getEntry(LineAddress), " \
                          f"tbe){self.end}"
                op_str += f"{self.nl}{Util.gen_progress_str(self, True)}"
            elif access_type == "evict":
                op_str += f"{self.nl}{self.open_template('forward_eviction.sm')}"
                evict_states = Util.get_evict_trans_states(arch)
                if transitions[0].final_state in evict_states:
                    op_str += f"{self.nl}{Util.gen_silent_evict(self)}"
                else:
                    op_str += f"{self.nl}{Util.gen_progress_str(self, True)}"


            elif access_type != "evict" and not is_hit and state_name not in invalid_states:
                # If the access was a load or a store we should now pop the queue to indicate we've handled it,
                # EXCEPT if we needed to allocate a cache entry or perform a local hit callback,
                # in which case the triggered transition should pop the queue instead.
                op_str += f"{self.nl}{GenPCCToSLICC.gen_pop_net(self, 'mandatory_in')}"
                op_str += f"{self.nl}{Util.gen_progress_str(self, True)}"

            else:
                # Also add a dummy event to make sure the simulation makes progress
                op_str += f"{self.nl}{Util.gen_progress_str(self, True)}"

            op_str = self.add_tabs(op_str, 1)

            transition_str = f"if (st == State:{state_name}) {{{self.nl}{op_str}{self.nl}}}"
            transitions_strs.append(transition_str)

        return self.add_tabs(" else ".join(transitions_strs)
                             + f" else {{{self.nl}"
                             + f"{self.add_tabs(Util.gen_recycle_str(self, True, 'mandatory_in'), 1)}{self.nl}}}",
                             indent_level)
