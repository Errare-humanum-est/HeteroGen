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

from typing import List, Dict, Tuple, Union, Set

from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess
from DataObjects.ClassSystemTuple import SystemTuple
from DataObjects.ClassMultiDict import MultiDict
from DataObjects.FlowDataTypes.ClassMessage import Message, BaseMessage
from DataObjects.ClassTrace import Trace
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.States.ClassStatev2 import State_v2

from networkx import MultiDiGraph
from Algorithms.ControllerGeneration.NetworkxGeneral.TreeCopyNetworkx import TreeCopyNetworkx

from Debug.Monitor.ClassDebug import Debug


class MsgTraceMap:
    def __init__(self, msg: Message, access_trace: Trace, dir_trace: Trace):
        self.msg: Message = msg
        self.access_trace = access_trace
        self.dir_trace = dir_trace

    def __str__(self):
        return str(self.msg)

    def __hash__(self):
        in_tuple = (hash(in_msg) for in_msg in self.dir_trace.guards_msg)
        out_tuple = (hash(out_msg) for out_msg in self.dir_trace.out_msg)
        return hash((hash(self.msg), in_tuple, out_tuple))


class StateTransactionCompl(TreeCopyNetworkx, Debug):
    def __init__(self, allowed_state_tuple_list: List[SystemTuple], directory: FlatArchitecture):
        TreeCopyNetworkx.__init__(self)
        Debug.__init__(self, True)

        self.prune_operation_flag: bool = False

        self.directory = directory

        self.allowed_state_tuples: List[SystemTuple] = allowed_state_tuple_list

        # Determine missing incoming request traces for the stable states
        self.access_state_map = self.gen_directory_stable_state_guard_map()
        self.access_state_map_miss = self.get_missing_directory_transactions(self.access_state_map)

        self.guard_request_map = self.gen_access_directory_message_map()
        self.dir_state_connectivity_map = self.get_state_access_connectivity_map()

        # Autocomplete the missing directory transactions
        self.auto_complete_directory_transactions()

    # Returns message to directory state mapping
    def gen_directory_stable_state_guard_map(self) -> MultiDict:
        access_state_map = MultiDict()
        for transition in self.directory.get_architecture_transitions():
            if transition.start_state in self.directory.stable_states:
                if (transition.guard not in access_state_map or
                        transition.start_state not in access_state_map[transition.guard]):
                    access_state_map[transition.guard] = transition.start_state

        return access_state_map

    # Derive for which directory states the messages are not defined
    def get_missing_directory_transactions(self, access_state_map: MultiDict):
        access_state_missing_map = MultiDict()
        for access in access_state_map:
            for stable_state in self.directory.stable_states:
                if stable_state not in access_state_map[access]:
                    access_state_missing_map[access] = stable_state

        return access_state_missing_map

    # Returns request to directory incoming message mapping
    def gen_access_directory_message_map(self) -> MultiDict:
        guard_request_map = MultiDict()
        for state_tuple in self.allowed_state_tuples:

            access_traces = state_tuple.get_arch_access_trace()
            # If multiple concurrent accesses happen skip the allowed state tuple
            if len(access_traces) > 1:
                continue

            dir_traces = state_tuple.get_arch_traces(self.directory)
            # If multiple concurrent accesses happen skip the allowed state tuple
            self.perror("If only a single access happens multiple directory traces ""are illegal internal model" 
                        "checker error", len(dir_traces) < 2)

            if not access_traces:
                continue

            access_out_msg_set = set([str(out_msg) for out_msg in access_traces[0].out_msg])
            dir_trace_messages = set([str(in_msg) for dir_trace in dir_traces for in_msg in dir_trace.guards_msg])

            msg_intersect = access_out_msg_set.intersection(dir_trace_messages)
            if not msg_intersect:
                continue

            for msg in access_traces[0].out_msg:
                if str(msg) in msg_intersect:
                    if (not str(access_traces[0].init_guard) in guard_request_map or
                            msg.base_msg not in guard_request_map[str(access_traces[0].init_guard)]):
                        guard_request_map[str(access_traces[0].init_guard)] = msg.base_msg

        return guard_request_map

    def get_state_access_connectivity_map(self) -> MultiDict:
        state_connectivity_map: MultiDict = MultiDict()

        for state_tuple in self.allowed_state_tuples:
            access_traces = state_tuple.get_arch_access_trace()
            # If multiple concurrent accesses happen skip the allowed state tuple
            if len(access_traces) > 1:
                continue

            dir_traces = state_tuple.get_arch_traces(self.directory)
            if not dir_traces:
                continue

            # If multiple concurrent accesses happen skip the allowed state tuple
            self.perror("If only a single access happens multiple directory traces ""are illegal internal model" 
                        "checker error", len(dir_traces) < 2)

            # Ignore loops
            if dir_traces[0].start_state == dir_traces[0].final_state:
                continue

            if not access_traces:
                Debug.pwarning("No access trace found for system tuple: " + str(state_tuple))
                continue

            # Evicts are not considered relevant for the connectivity map as evicts are only performed in case a
            # cache runs out of space, but not because another cache wants to perform an operation
            if (isinstance(access_traces[0].init_guard, BaseAccess.Access) and
                    (dir_traces[0].start_state not in state_connectivity_map or
                     dir_traces[0].final_state not in state_connectivity_map[dir_traces[0].start_state])):
                state_connectivity_map[dir_traces[0].start_state] = dir_traces[0].final_state

        return state_connectivity_map

    # Checks if the messages are unique to the accesses
    def check_access_message_mapping(self, guard_request_map: MultiDict):
        for cur_guard_message_list in guard_request_map.values():
            for ref_guard_message_list in guard_request_map.values():
                if cur_guard_message_list == ref_guard_message_list:
                    continue
                if set(cur_guard_message_list).intersection(set(ref_guard_message_list)):
                    self.perror("Different accesses use the same message names, unable to resolve accesses "
                                "in case of concurrency: " + str(set(cur_guard_message_list)) +
                                " | " + str(set(ref_guard_message_list)))

    def auto_complete_directory_transactions(self) -> List[Transition_v2]:
        new_trans = []
        for missing_access in self.access_state_map_miss:
            miss_states = self.access_state_map_miss[missing_access]

            # Get the guard of the message and complementary messages
            guard, complementary_msgs = self.get_guard_of_missing_message(missing_access)

            if not complementary_msgs:
                continue

            for miss_state in miss_states:
                complementary_trans = self.find_complementary_transition(miss_state, missing_access, complementary_msgs)
                new_trans += complementary_trans

        return new_trans

    def get_guard_of_missing_message(self, miss_msg: BaseMessage) -> Tuple[str, List[str]]:
        for guard in self.guard_request_map:
            if miss_msg in self.guard_request_map[guard]:
                ret_alternative_msg_list: List[str] = copy.copy(self.guard_request_map[guard])
                ret_alternative_msg_list.remove(miss_msg)
                return guard, ret_alternative_msg_list
            # Evicts are not auto completed at the directory level, because in some states evicts are prohibited,
            # writing evicts requires detailed knowledge of the SSP that cannot be easily inferred
            elif guard in BaseAccess.Evict_str_list:
                return guard, []
        self.perror("No guard could be assigned to missing message: " + str(miss_msg))

    def find_complementary_transition(self,
                                      state: State_v2,
                                      missing_guard: BaseMessage,
                                      compl_msgs: List[str]) -> List[Transition_v2]:
        compl_trace: List[Trace] = []
        compl_guards: List[str] = []

        new_transition_set: Set[Transition_v2] = set()

        for allowed_tuple in self.allowed_state_tuples:
            dir_trace = self.extract_dir_trace(allowed_tuple)

            # If no directory trace was found continue
            if (not dir_trace or
                    dir_trace.start_state != state or
                    str(dir_trace.init_guard) not in [str(msg) for msg in compl_msgs]):
                continue

            # Record the found complementary guards
            if str(dir_trace.init_guard) not in compl_guards:
                compl_guards.append(str(dir_trace.init_guard))

            # If multiple guards are detected then only the ssp_transitions related to the first guard
            if str(dir_trace.init_guard) == compl_guards[0]:
                compl_trace.append(dir_trace)

        if len(compl_guards) == 0:
            # No directory trace was found defined for state that is complementary to initial access, hence try to mimic
            # default behaviour
            self.pwarning("No complementary ssp_transitions for guard " + str(missing_guard) + " found in state "
                          + str(state))
            self.pwarning("In case of model checker failure, please define behaviour for guard")

            # The auxiliary states are protected from change.
            compl_trace = self.get_default_traces(state, missing_guard)
            self.gen_new_access_graph(state, compl_trace[0])

        else:
            # Multiple complementary guards are defined for same access, so throw a warning and choose one
            # Auxiliary states must be checked to verify in which state the cache issuing the request was when
            # trying to perform the access
            if len(compl_guards) > 1:
                self.pwarning("Multiple complementary ssp_transitions for same access type found in state "
                              + str(state))
                self.pwarning("In case of model checker failure, please define behaviour for "
                              + str(missing_guard) + "in state " + str(state) + " manually in the SSP as the automatic "
                                                                                "resolution might fail")
            # Generate new ssp_transitions
            self.gen_new_access_transition(missing_guard, compl_trace[0])

        return list(new_transition_set)

    def extract_dir_trace(self, state_tuple: SystemTuple) -> Union[Trace, None]:
        access_traces = state_tuple.get_arch_access_trace()
        # If multiple concurrent accesses happen skip the allowed state tuple
        if len(access_traces) > 1:
            return None

        dir_traces = state_tuple.get_arch_traces(self.directory)
        # If multiple concurrent accesses happen skip the allowed state tuple
        self.perror("If only a single access happens multiple directory traces ""are illegal internal model"
                    "checker error", len(dir_traces) < 2)

        if dir_traces:
            return dir_traces[0]

        return None

    def get_default_traces(self, cur_state: State_v2, cur_guard: BaseMessage) -> List[Trace]:
        dir_state_trace_dict = MultiDict()
        dir_stable_state = self.access_state_map[cur_guard]

        for state_tuple in self.allowed_state_tuples:
            access_traces = state_tuple.get_arch_access_trace()
            # If multiple concurrent accesses happen skip the allowed state tuple
            if len(access_traces) > 1:
                continue

            dir_traces = state_tuple.get_arch_traces(self.directory)
            # If multiple concurrent accesses happen skip the allowed state tuple
            self.perror("If only a single access happens multiple directory traces ""are illegal internal model" 
                        "checker error", len(dir_traces) < 2)

            if (not dir_traces or
                    dir_traces[0].init_guard != cur_guard or
                    dir_traces[0].start_state not in dir_stable_state):
                continue

            # A default behaviour has been found
            dir_state_trace_dict[dir_traces[0].start_state] = dir_traces[0]

        self.perror("No default trace for access could be automatically detected for guard " + str(cur_guard) +
                    " in state " + str(dir_stable_state), dir_state_trace_dict)

        state_list = sorted(list(dir_state_trace_dict.keys()), key=lambda state: str(state))

        replication_state = state_list[0]

        if len(state_list) > 1:
            # Replicate evict behaviour that is closest to the original access permissions of the cache.
            # This can be achieved by starting in original start state and perform an exhaustive search until the first
            # remote state is found
            # E.g. PutM in O state where PutO is defined for O state and PutS for S state
            replication_state = self.get_replication_state(cur_state, state_list)
            self.pwarning("Multiple default states: " + str(state_list) +
                          "found for which behaviour of directory for incoming request: " + str(cur_guard) +
                          "is defined. Replicating behaviour defined for state: " + str(state_list[0]),
                          len(state_list) > 1)

        return dir_state_trace_dict[replication_state]

    ## If a definition of a guard is missing in a specific state an auto-completion is attempted based on the idea,
    #  that the state closest to the original state in which the request is performed exhibits the correct behaviour
    def get_replication_state(self, start_state: State_v2, replication_states: List[State_v2]) -> State_v2:
        next_state_list = [start_state]
        served_state_list = []

        while next_state_list:
            state = next_state_list[0]

            if state in replication_states:
                return state
            self._get_next_connectivity_states(state, next_state_list, served_state_list)

        return replication_states[0]

    def _get_next_connectivity_states(self,
                                      cur_state: State_v2,
                                      next_state_list: List[State_v2],
                                      served_state_list: List[State_v2]):
        next_state_list.remove(cur_state)
        served_state_list.append(cur_state)
        for new_next_state in self.dir_state_connectivity_map[cur_state]:
            if new_next_state not in served_state_list:
                next_state_list.append(new_next_state)

    def gen_new_access_transition(self,
                                  new_guard: BaseMessage,
                                  compl_trace: Trace):

        sub_trees = list(self.directory.state_sub_tree_dict[compl_trace.start_state])

        for sub_tree in sub_trees:
            out_transitions = [edge_tuple[2]
                               for edge_tuple in list(sub_tree.out_edges(compl_trace.start_state, data="transition"))]
            if str(out_transitions[0].guard) == str(compl_trace.init_guard):
                new_out_transitions = self.copy_graph_exist_transitions(out_transitions,
                                                                        new_guard,
                                                                        compl_trace.init_guard)

                new_graph = self.deepcopy_graph(sub_tree)

                for out_transition in out_transitions:
                    new_graph.remove_edge(out_transition.start_state, out_transition.final_state)

                for new_out_transition in new_out_transitions:
                    new_graph.add_edge(new_out_transition.start_state,
                                       new_out_transition.final_state,
                                       transition=new_out_transition)

                # Safe new graph to directory, this also registers the new ssp_transitions for legacy purpose
                self.directory.add_tree_to_arch(new_graph)
        return

    @staticmethod
    def copy_graph_exist_transitions(transitions: List[Transition_v2],
                                     new_guard: BaseMessage,
                                     cur_guard: BaseMessage) -> List[Transition_v2]:
        new_trans_list: List[Transition_v2] = []
        for trans in transitions:
            new_trans = trans.deepcopy_trans()
            new_trans.guard = new_guard
            new_trans.rename_operation(str(cur_guard), str(new_guard))
            new_trans_list.append(new_trans)

        return new_trans_list

    def gen_new_access_graph(self, new_state: State_v2, compl_trace: Trace):

        sub_trees = self.directory.state_sub_tree_dict[compl_trace.start_state]

        for sub_tree in sub_trees:
            out_transitions = [edge_tuple[2]
                               for edge_tuple in list(sub_tree.out_edges(compl_trace.start_state, data="transition"))]
            if str(out_transitions[0].guard) == str(compl_trace.init_guard):
                self.copy_state_graph(sub_tree, new_state)

        return

    def copy_state_graph(self, sub_graph: MultiDiGraph, new_state: State_v2):
        # Create a deepcopy of the graph
        new_graph = self.deepcopy_graph(sub_graph)
        # Get the root and terminal nodes
        root_node = self.get_root_node_by_attribute(new_graph)
        terminal_nodes = self.get_terminal_nodes_by_attribute(new_graph)

        state_map_dict: Dict[State_v2, State_v2] = {}
        # If a transaction is not defined all incoming requests are invalid so they will only loop
        for transition in self.get_transitions_from_graph(new_graph):

            if transition.start_state not in state_map_dict:
                if transition.start_state == root_node:
                    state_map_dict[transition.start_state] = new_state
                else:
                    state_map_dict[transition.start_state] = self.replace_state(new_state, transition.start_state)

            if transition.final_state not in state_map_dict:
                if transition.final_state in terminal_nodes:
                    # All outdated ssp_transitions do not change the directory state, therefore loop
                    state_map_dict[transition.final_state] = new_state
                else:
                    state_map_dict[transition.final_state] = self.replace_state(new_state, transition.final_state)

        # Update all states in the graph, this also updates the root and terminal nodes
        new_graph = self.update_graph_states(new_graph, state_map_dict)

        # Safe new graph to directory
        self.directory.add_tree_to_arch(new_graph)

        # Technically it would be valid to strip all internal operations away apart from conditions...

    @staticmethod
    def replace_state(new_start_state: State_v2, transition_state: State_v2) -> Union[State_v2, None]:
        new_state_name = str(new_start_state) + "_x_" + str(transition_state)
        new_state = State_v2(new_state_name)

        # The new state has no start state set as the directory is point of serialization, the end state set of the
        # new_transition state becomes the end state set of the new start state
        for end_state_set in set(new_start_state.end_state_set):
            end_state_set.add_end_state(new_state)

        return new_state

    def prune_operations(self):
        pass
