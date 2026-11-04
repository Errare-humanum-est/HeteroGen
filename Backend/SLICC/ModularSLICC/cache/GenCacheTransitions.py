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

from collections import OrderedDict

from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from Backend.SLICC.ModularSLICC.common.GenMachineActions import GenMachineActions
from Backend.SLICC.ModularSLICC.common.GenMachineTransitions import GenMachineTransitions
from Backend.SLICC.ModularSLICC.common import Util


class GenCacheTransitions(TemplateHandler):

    def __init__(self, handler_dir: str):
        TemplateHandler.__init__(self, handler_dir)

    def gen_cache_transitions_str(self, arch: FlatArchitecture, in_ports: 'OrderedDict[str, str]') -> str:

        invalid_states = {str(state) for state in Util.get_invalid_states(arch)}
        invalid_states_str = f"{{{', '.join(invalid_states)}}}"
        all_states = {str(state) for state in arch.get_architecture_states_verified()}
        all_states_str = f"{{{', '.join(all_states)}}}"

        dealloc_trans_strs = []
        stall_strs = [GenMachineTransitions.gen_stall_transition(self, all_states, "mandatory_in")]
        for port_name in sorted(in_ports.values()):
            dealloc_trans_strs.append(self.string_repl_keys(self.open_template("transition_dealloc_entry.sm"),
                                                            [invalid_states_str,
                                                             port_name,
                                                             GenMachineActions.get_queue_pop_action_name(port_name)
                                                             ]
                                                            )
                                      )
            stall_strs.append(GenMachineTransitions.gen_stall_transition(self, all_states, port_name))

        dealloc_trans_str = (self.nl * 2).join(dealloc_trans_strs)
        stall_str = (self.nl * 2).join(stall_strs)

        alloc_trans_strs = []
        next_states = {str(state) for state in Util.get_states_following_invalid_states(arch)}
        for next_state in next_states:
            for state in invalid_states:
                alloc_trans_strs.append(self.string_repl_keys(self.open_template("transition_alloc_entry.sm"),
                                                              [state,
                                                               next_state,
                                                               GenMachineActions.get_operation_action_name(state,
                                                                                                         next_state
                                                                                                         ),
                                                               ]
                                                              )
                                        )
        alloc_trans_str = (self.nl * 2).join(alloc_trans_strs)

        local_hit_trans_strs = []
        local_hit_map = Util.get_local_hit_events(arch)
        for (access, start_state), (end_state, event_name) in sorted(local_hit_map.items()):
            local_hit_trans_strs.append(self.string_repl_keys(self.open_template("transition_local_hit.sm"),
                                                              [start_state, event_name, end_state, access]
                                                              )
                                        )
        local_hit_trans_str = (self.nl * 2).join(local_hit_trans_strs)

        remote_hit_trans_strs = []
        for in_port in sorted(in_ports.values()):
            remote_hit_map = Util.get_remote_hit_events_port(arch, in_port)
            for (access, end_state), event_name in sorted(remote_hit_map.items()):
                remote_hit_trans_strs.append(self.string_repl_keys(self.open_template("transition_remote_hit.sm"),
                                                                   [end_state, event_name, access, in_port]
                                                                   )
                                             )
        remote_hit_trans_str = (self.nl * 2).join(remote_hit_trans_strs)

        return "//" + __name__ + self.nl \
               + dealloc_trans_str + (self.nl * 2) \
               + alloc_trans_str + (self.nl * 2) \
               + local_hit_trans_str + (self.nl * 2) \
               + remote_hit_trans_str + (self.nl * 2) \
               + stall_str + (self.nl * 2) \
               + self.string_repl_keys(self.open_template("transition_alloc_tbe.sm"), [all_states_str]) \
               + (self.nl * 2) \
               + self.string_repl_keys(self.open_template("transition_dealloc_tbe.sm"), [all_states_str]) \
               + (self.nl * 2)  \
               + GenMachineTransitions.gen_progress_transition(
                    self, map(str, arch.get_architecture_states_verified())) + self.nl
