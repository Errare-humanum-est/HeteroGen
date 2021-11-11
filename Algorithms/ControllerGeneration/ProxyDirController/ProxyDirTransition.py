#  Copyright (c) 2021.  Nicolai Oswald
#  Copyright (c) 2021.  University of Edinburgh
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
import copy
from typing import Tuple, Dict, List
from antlr3.tree import CommonTree

from Algorithms.General.AuxStateHandler import AuxStateHandler
from Parser.ProtoCCcomTreeFct import toStringList

from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase


from DataObjects.ClassTrace import Trace
from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.States.ProxyDirState import ProxyDirState
from DataObjects.ClassSystemTuple import SystemTuple
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture

from Debug.Monitor.ClassDebug import Debug


class ProxyDirTransition(Transition_v2):

    def __init__(self,
                 proxy_dir_trans_cluster: List[Transition_v2],
                 system_tuple: SystemTuple,
                 cache_arch: FlatArchitecture,
                 dir_arch: FlatArchitecture,
                 proxy_dir_states: Dict[str, ProxyDirState],
                 proxy_dir_start_state: ProxyDirState = None):

        self.proxy_trans_cluster = proxy_dir_trans_cluster

        self.proxy_state_tuple, self.dir_state_tuple = self.get_proxy_dir_states(proxy_dir_trans_cluster,
                                                                                 system_tuple,
                                                                                 cache_arch,
                                                                                 dir_arch,
                                                                                 proxy_dir_start_state)

        start_state, final_state = self.gen_start_end_state(system_tuple,
                                                            cache_arch,
                                                            dir_arch,
                                                            proxy_dir_states,
                                                            proxy_dir_start_state)

        # Generate new transition
        trans_copy = [copy.copy(trans) for trans in proxy_dir_trans_cluster]
        proxy_trans: Transition_v2 = self.merge_proxy_dir_transitions(trans_copy)[0]
        proxy_trans.start_state = start_state
        proxy_trans.final_state = final_state

        Transition_v2.__init__(self, start_state, final_state,
                               proxy_trans.operations, proxy_trans.guard, proxy_trans.out_msg, proxy_trans.out_event)

        # Inherit newly generated transition parameters
        self.start_state.add_transition(self)


    def __str__(self):
        return super().__str__()

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return super().__eq__(other)

    def get_proxy_dir_states(self,
                             proxy_dir_trans_cluster: List[Transition_v2],
                             system_tuple: SystemTuple,
                             cache_arch: FlatArchitecture,
                             dir_arch: FlatArchitecture,
                             proxy_dir_start_state: ProxyDirState = None
                             ):
        proxy_state_tuple: Tuple[State_v2] = self.get_start_final_state(
            proxy_dir_trans_cluster,
            system_tuple.get_arch_access_trace(cache_arch)[0])
        if not proxy_state_tuple:
            proxy_state_tuple = (proxy_dir_start_state.proxy_state, proxy_dir_start_state.proxy_state)

        dir_state_tuple = None
        dir_trace = system_tuple.get_arch_traces(dir_arch)
        if dir_trace:
            dir_state_tuple: Tuple[State_v2] = self.get_start_final_state(proxy_dir_trans_cluster,
                                                                          dir_trace[0])

        if proxy_dir_start_state and not dir_state_tuple:
                dir_state_tuple = (proxy_dir_start_state.dir_state, proxy_dir_start_state.dir_state)

        if not dir_state_tuple:
            dir_state_tuple: Tuple[State_v2] = (system_tuple.get_arch_machines(dir_arch)[0].start_state,
                                                system_tuple.get_arch_machines(dir_arch)[0].final_state)

        return proxy_state_tuple, dir_state_tuple

    def gen_start_end_state(self,
                            system_tuple: SystemTuple,
                            cache_arch: FlatArchitecture,
                            dir_arch: FlatArchitecture,
                            proxy_dir_states: Dict[str, ProxyDirState],
                            proxy_dir_start_state: ProxyDirState = None
                            ):

        # Cover the proxy transition start and final state
        if not proxy_dir_start_state:
            start_state = self.dir_state_tuple[0]
        else:
            start_state = proxy_dir_start_state

        # If the proxy has already reached a final state
        if self.proxy_state_tuple[1] in [mach.final_state for mach in system_tuple.get_arch_machines(cache_arch)]\
                and self.dir_state_tuple[1] in [mach.final_state for mach in system_tuple.get_arch_machines(dir_arch)]:
            final_state = self.dir_state_tuple[1]
        else:
            # The new final state has to be created/generated
            new_final_state = ProxyDirState(self.proxy_state_tuple[1], self.dir_state_tuple[1])

            # Check if the new final_state_tuple already exists
            if str(new_final_state) in proxy_dir_states:
                final_state = proxy_dir_states[str(new_final_state)]
            else:
                proxy_dir_states[str(new_final_state)] = new_final_state
                final_state = new_final_state

        return start_state, final_state

    @staticmethod
    def get_start_final_state(proxy_dir_trans_cluster: List[Transition_v2],
                              mach_trace: Trace):
        trans_list = [trans for trans in proxy_dir_trans_cluster if trans in mach_trace.trace_trans]
        if trans_list:
            start_state = trans_list[0].start_state
            final_state = trans_list[-1].final_state
            return start_state, final_state
        else:
            return None

    def merge_proxy_dir_transitions(self, proxy_dir_transitions: List[Transition_v2]) -> List[Transition_v2]:
        # Move copy here
        cur_transitions = proxy_dir_transitions
        merge_found = 1
        while merge_found:
            merge_found = 0
            new_cur_transitions = []
            for transition_ind in range(0, len(cur_transitions)):
                prev_transition = cur_transitions[transition_ind]
                if transition_ind + 1 < len(cur_transitions):
                    next_transition = cur_transitions[transition_ind + 1]
                    merged_transition = self.try_merge_proxy_dir_transition(prev_transition, next_transition)

                    if merged_transition:
                        merge_found = 1
                        new_cur_transitions.append(merged_transition)
                        next_trans_ind = cur_transitions.index(next_transition) + 1
                        if next_trans_ind < len(cur_transitions):
                            new_cur_transitions += cur_transitions[next_trans_ind:len(cur_transitions)]
                        break

                new_cur_transitions.append(prev_transition)
            cur_transitions = new_cur_transitions

        return cur_transitions

    def try_merge_proxy_dir_transition(self, prev_transition: Transition_v2,
                                       next_transition: Transition_v2) -> Transition_v2:
        prev_transition = prev_transition.deepcopy_trans()
        next_transition = next_transition.deepcopy_trans()

        inmsg_str = str(next_transition.guard)
        outmsg_str_list = [str(out_msg) for out_msg in prev_transition.out_msg]
        if prev_transition.out_event:
            outmsg_str_list.append(str(prev_transition.out_event))

        if inmsg_str not in outmsg_str_list:
            Debug.perror("New ProxyTransition generation failed. ProxyDirController generates wrong transition tuples")

        # remove index from outMsg list
        remove_msg = prev_transition.out_msg.pop(outmsg_str_list.index(inmsg_str))

        remove_operation = self.find_assign_msg_by_str(remove_msg, prev_transition)
        msg_var_name = str(remove_operation[0].children[0])
        msg_name = str(remove_operation[1][0])
        new_msg_var_name = msg_var_name + "_" + msg_name
        remove_send_func = self.remove_send_func(remove_operation[0], prev_transition)

        # Update the variable name to avoid it to be overwritten
        AuxStateHandler.save_rename_var(prev_transition.operations, remove_operation[0], msg_var_name,
                                        new_msg_var_name)

        # Update all operations that were using the previously received message
        # Reassign variable in output function
        AuxStateHandler.cond_operations_var_rename(next_transition.operations,
                                                   str(remove_operation[1][0]),
                                                   new_msg_var_name)

        # Update the initial guard operation is removed when merging two transitions
        if len(next_transition.operations) > 1:
            prev_transition.operations += next_transition.operations[1:]
        prev_transition.out_msg += next_transition.out_msg

        if next_transition.out_event:
            Debug.perror("Multiple out events per transition required", not prev_transition.out_event)
            prev_transition.out_event = next_transition.out_event

        prev_transition.final_state = next_transition.final_state

        return prev_transition

    @staticmethod
    def find_assign_msg_by_str(msg_str: str, transition: Transition_v2) -> Tuple[CommonTree, List[CommonTree]]:
        for operation in transition.operations:
            children = operation.children
            if str(operation) == ProtoParserBase.k_assign and str(children[2]) == ProtoParserBase.k_msg:
                if str(msg_str) in toStringList(children[2]):
                    return operation, [children[2].children[1]]

    @staticmethod
    def remove_send_func(assign_operation: CommonTree, transition: Transition_v2) -> CommonTree:
        msg_var_name = str(assign_operation.children[0])
        var_assigned: bool = False
        for operation in transition.operations:
            if id(operation) == id(assign_operation):
                var_assigned = True
            if var_assigned and str(operation) == ProtoParserBase.k_send:
                if str(operation.children[1]) == str(msg_var_name):
                    return transition.operations.pop(transition.operations.index(operation))
            elif var_assigned and str(operation) in ProtoParserBase.kmbcast:
                Debug.perror("Multicast or Broadcast transition merging not supported")
