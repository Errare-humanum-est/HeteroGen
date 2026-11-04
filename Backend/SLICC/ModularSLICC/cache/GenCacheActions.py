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

import re
from collections import OrderedDict

from DataObjects.ClassCluster import Cluster
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.ClassMultiDict import MultiDict
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from Backend.SLICC.ModularSLICC.common.GenMachineActions import GenMachineActions
from Backend.SLICC.ModularSLICC.common import Util
from Backend.SLICC.ModularSLICC.common.GenSLICCTree import GenSLICCTree


class GenCacheActions(TemplateHandler):

    def __init__(self, handler_dir: str):
        TemplateHandler.__init__(self, handler_dir)
        self.generated_action_shorthands = set()

    def gen_cache_actions_str(self, cluster: Cluster, arch: FlatArchitecture, in_ports: 'OrderedDict[str, str]',
                              out_ports: 'OrderedDict[str, str]') -> str:

        # We only need to generate actions corresponding to the operations in a transition
        # for transitions which require allocating a new cache entry (i.e. ones starting
        # in an invalid/not-present state). The rest of the controller will be defined
        # in the in_port definition.
        op_actions = []
        invalid_states = Util.get_invalid_states(arch)
        access_transitions = {access: MultiDict() for access in ["load", "store"]}
        for state in invalid_states:
            for trans in state.getaccessmiss():
                access = trans.guard
                access = str(access)
                access_transitions[access][str(state)] = trans
        for _, state_map in sorted(access_transitions.items()):
            for state, transitions in sorted(state_map.items()):
                slicc_tree_gen = GenSLICCTree(cluster, arch, "", out_ports, allow_port_popping=False,
                                              set_final_state=False)
                op_str = slicc_tree_gen.gen_slicc_tree(transitions)
                if re.search(r"\bLineAddress\b", op_str) is not None:
                    # If we reference the LineAddress, we need to bring it into scope from the in_msg first
                    op_str = f"Addr LineAddress := in_msg.LineAddress{self.end}" + op_str
                if re.search(r"\bentry\b", op_str) is not None:
                    # Need to add a renaming of cache_entry to entry
                    op_str = f"Entry entry := cache_entry{self.end}" + op_str
                # Assert all the transitions have the same end state, otherwise I don't know what to do...
                next_state = str(transitions[0].final_state)
                assert all(str(trans.final_state) == next_state for trans in transitions)
                action_name = GenMachineActions.get_operation_action_name(str(state), next_state)
                shorthand = self._gen_operation_action_shorthand(str(state), next_state)
                op_actions.append(self.string_repl_keys(self.open_template("cache_peek_mandatory_action.sm"),
                                                        [action_name, shorthand, self.add_tabs(op_str, 2)]
                                                        )
                                  )

        port_actions = [
            GenMachineActions.gen_pop_action(
                self, "mandatory_in", self._gen_queue_pop_action_shorthand("mandatory_in")),
            GenMachineActions.gen_recycle_action(
                self, "mandatory_in", self._gen_recycle_action_shorthand("mandatory_in")),
        ]
        for port_name in sorted(in_ports.values()):
            port_actions.append(
                GenMachineActions.gen_pop_action(self, port_name, self._gen_queue_pop_action_shorthand(port_name)))
            port_actions.append(
                GenMachineActions.gen_recycle_action(self, port_name, self._gen_recycle_action_shorthand(port_name)))

        active_cache_line = Util.get_active_cache_line(arch)

        return "//" + __name__ + self.nl \
               + self.open_template("action_alloc_entry.sm") + self.nl \
               + self.open_template("action_dealloc_entry.sm") + self.nl \
               + self.open_template("action_alloc_tbe.sm") + self.nl \
               + self.open_template("action_dealloc_tbe.sm") + self.nl \
               + self.string_repl_keys(self.open_template("action_cache_local_load_hit.sm"), [active_cache_line]) + self.nl \
               + self.string_repl_keys(self.open_template("action_cache_local_store_hit.sm"), [active_cache_line]) + self.nl \
               + self.string_repl_keys(self.open_template("action_cache_remote_load_hit.sm"), [active_cache_line]) + self.nl \
               + self.string_repl_keys(self.open_template("action_cache_remote_store_hit.sm"), [active_cache_line]) + self.nl \
               + (self.nl * 2).join(port_actions) + (self.nl * 2) \
               + (self.nl * 2).join(op_actions) + (self.nl * 2) \
               + GenMachineActions.gen_empty_action(self) + self.nl

    def _gen_operation_action_shorthand(self, start_state: str, end_state: str) -> str:
        action_shorthand = f'"{start_state[0]}{end_state[0]}0"'
        i = 0
        while action_shorthand in self.generated_action_shorthands:
            i += 1
            action_shorthand = action_shorthand[: -2] + str(i) + '"'
        self.generated_action_shorthands.add(action_shorthand)
        return action_shorthand

    def _gen_queue_pop_action_shorthand(self, port_name: str) -> str:
        action_shorthand = f'"p{port_name}0"'
        i = 0
        while action_shorthand in self.generated_action_shorthands:
            i += 1
            action_shorthand = action_shorthand[: -2] + str(i) + '"'
        self.generated_action_shorthands.add(action_shorthand)
        return action_shorthand

    def _gen_recycle_action_shorthand(self, port_name: str) -> str:
        # TODO this method and the two above it should really be rewritten as one
        action_shorthand = f'"r{port_name}0"'
        i = 0
        while action_shorthand in self.generated_action_shorthands:
            i += 1
            action_shorthand = action_shorthand[: -2] + str(i) + '"'
        self.generated_action_shorthands.add(action_shorthand)
        return action_shorthand
