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

from typing import Dict
from collections import OrderedDict

from DataObjects.ClassCluster import Cluster
from DataObjects.ClassMultiDict import MultiDict
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from Backend.SLICC.ModularSLICC.common.GenMachineInPorts import GenMachineInPorts
from Backend.SLICC.ModularSLICC.common import Util
from Backend.SLICC.ModularSLICC.common.GenPCCToSLICC import GenPCCToSLICC
from Backend.SLICC.ModularSLICC.common.GenSLICCTree import GenSLICCTree


class GenCacheInPorts(TemplateHandler):

    def __init__(self, handler_dir: str):
        TemplateHandler.__init__(self, handler_dir)
        self.all_message_names = set()

    def gen_cache_in_ports_str(
            self,
            cluster: Cluster,
            arch: FlatArchitecture,
            in_ports: 'OrderedDict[str, str]',
            out_ports: 'OrderedDict[str, str]'
    ) -> str:

        return "//" + __name__ + self.nl \
               + GenMachineInPorts.gen_machine_in_ports(
                    self, cluster, arch, in_ports, out_ports) \
               + self.nl + self._gen_mandatory_in_port(cluster, arch, out_ports) + self.nl

    def _gen_mandatory_in_port(self, cluster: Cluster, arch: FlatArchitecture,
                               out_ports: 'OrderedDict[str, str]') -> str:

        access_transitions = {access: MultiDict() for access in ["load", "store", "evict"]}
        for state in arch.get_architecture_states_verified():
            for trans in state.getaccessmiss():
                access = trans.guard
                access = str(access)
                assert (True, str(state)) not in access_transitions[access], \
                    f"Cannot both hit and miss the same access in the same state ({access},{str(state)})."
                access_transitions[access][(False, str(state))] = trans
            for trans in state.getaccesshit():
                access = trans.guard
                access = str(access)
                assert (False, str(state)) not in access_transitions[access], \
                    f"Cannot both hit and miss the same access in the same state ({access},{str(state)})."
                access_transitions[access][(True, str(state))] = trans
            evicts = state.getevict()
            if evicts:
                assert len(evicts) == 1, f"{evicts}"
                access_transitions['evict'][(False, str(state))] = evicts[0]
                # Note we treat all evicts like "misses" as they do not require a callback to the sequencer

        return self.string_repl_keys(self.open_template("mandatory_cpu_in_port.sm"),
                                     [self._gen_access_str(
                                         cluster, arch, access_transitions, out_ports, 4, "evict"),
                                      self._gen_access_str(
                                         cluster, arch, access_transitions, out_ports, 5, "load"),
                                      self._gen_access_str(
                                         cluster, arch, access_transitions, out_ports, 5, "store"),
                                      ]
                                     )

    def _gen_access_str(
            self,
            cluster: Cluster,
            arch: FlatArchitecture,
            transition_map: Dict[str, 'MultiDict'],
            out_ports: 'OrderedDict[str, str]',
            indent_level: int,
            access_type: str
    ) -> str:

        transition_map = transition_map[access_type]  # Other accesses handled separately

        transitions_strs = []
        hit_event_map = Util.get_local_hit_events(arch)
        invalid_states = {str(state) for state in Util.get_invalid_states(arch)}

        for (is_hit, state_name), transitions in transition_map.items():

            slicc_tree_gen = GenSLICCTree(cluster, arch, "mandatory_in", out_ports,
                                          allow_port_popping=False, set_final_state=(not is_hit))

            op_str = ""
            entry_alloced = False

            if state_name in invalid_states and access_type != "evict":
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
            else:
                op_str += slicc_tree_gen.gen_slicc_tree(transitions)

            if is_hit:
                assert not entry_alloced, "Can't both alloc entry and hit locally"
                _, event_name = hit_event_map[(access_type, state_name)]
                op_str += f"{self.nl}trigger(Event:{event_name}, LineAddress, getEntry(LineAddress), " \
                          f"tbe){self.end}"
            elif access_type == "evict":
                op_str += f"{self.nl}{self.open_template('forward_eviction.sm')}"

            if access_type != "evict" and not is_hit and state_name not in invalid_states:
                # If the access was a load or a store we should now pop the queue to indicate we've handled it,
                # EXCEPT if we needed to allocate a cache entry or perform a local hit callback,
                # in which case the triggered transition should pop the queue instead.
                op_str += f"{self.nl}{GenPCCToSLICC.gen_pop_net(self, 'mandatory_in')}"

            # Also add a dummy event to gen_make sure the simulation makes progress
            op_str += f"{self.nl}{Util.gen_progress_str(self, arch)}"

            op_str = self.add_tabs(op_str, 1)

            transition_str = f"if (st == State:{state_name}) {{{self.nl}{op_str}{self.nl}}}"
            transitions_strs.append(transition_str)

        return self.add_tabs(" else ".join(transitions_strs)
                             + f" else {{{self.nl}{self.tab}"
                             + f"{Util.gen_stall_str(self, arch, 'mandatory_in')}{self.nl}}}",
                             indent_level)
