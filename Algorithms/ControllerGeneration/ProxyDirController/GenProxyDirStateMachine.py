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

from typing import Tuple, Set, List, Dict
from itertools import combinations

from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.ClassLevel import Level
from Algorithms.ControllerGeneration.ProxyDirController.GenProxyCacheStateTuples import GenProxyCacheStateTuples
from DataObjects.ClassMultiDict import MultiDict

from Algorithms.ControllerGeneration.ProxyDirController.GenProxyCacheGraph import ProxyCacheGraph
from DataObjects.ClassSystemTuple import SystemTuple
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess
from DataObjects.States.ProxyDirState import ProxyDirState
from Algorithms.ControllerGeneration.ProxyDirController.ProxyDirTransition import ProxyDirTransition
from Algorithms.ControllerGeneration.General.ChainTransitions import ChainTransitions
from Algorithms.ControllerGeneration.NetworkxGeneral.TreeBaseNetworkx import TreeBaseNetworkx

from Algorithms.ControllerGeneration.NetworkxGeneral.CompoundStateGenNetworkx import CompoundStateGenNetworkx
from Debug.Monitor.ClassDebug import Debug
from DataObjects.FlowDataTypes.ClassEvent import Event


class ProxyDirStateMachine(TreeBaseNetworkx, GenProxyCacheStateTuples):

    def __init__(self, arch_level: Level):
        TreeBaseNetworkx.__init__(self)
        self.initial_arch_level = arch_level
        GenProxyCacheStateTuples.__init__(self, arch_level)

        self.proxy_dir_states: Dict[str, ProxyDirState] = {}
        self.proxy_dir_stable_states: Set[ProxyDirState] = set()

        # Generate the proxy dir transitions
        self.proxy_dir_trans = self.gen_proxy_access_cache_dir_controller()
        # Copy the event transitions of the proxy cache in reset state
        self.proxy_dir_trans.update(self.cache_initial_state_event_inheritance())
        # Copy the dir stable state architecture transitions
        self.proxy_dir_trans.update(self.initial_arch_level.directory.get_architecture_transitions())

    def gen_proxy_access_cache_dir_controller(self) -> Set[Transition_v2]:
        evict_proxy_dir_trans_dict: Dict[State_v2, Dict[State_v2, List[Tuple[ProxyDirTransition]]]] = \
            self.gen_evict_proxy_dir_trans_dict()
        access_proxy_dir_trans_dict: Dict[Tuple[State_v2, State_v2], List[Tuple[ProxyDirTransition]]] \
            = self.gen_access_proxy_dir_trans_dict()

        proxy_dir_trans: Set[ProxyDirTransition] = set()

        for cache_final_state, dir_final_state in access_proxy_dir_trans_dict:
            if dir_final_state in evict_proxy_dir_trans_dict[cache_final_state]:
                evict_traces = evict_proxy_dir_trans_dict[cache_final_state][dir_final_state]
            else:
                evict_traces = evict_proxy_dir_trans_dict[cache_final_state][list(evict_proxy_dir_trans_dict[
                                                                                      cache_final_state].keys())[0]]
            for evict_transition_trace in evict_traces:
                if len(evict_transition_trace) > 1:
                    proxy_dir_trans.update(evict_transition_trace[1:-1])

                for access_transition_trace in access_proxy_dir_trans_dict[(cache_final_state, dir_final_state)]:
                    if len(access_transition_trace) > 1:
                        proxy_dir_trans.update(access_transition_trace[0:-1])

                    if access_transition_trace[-1].dir_state_tuple[1] != \
                            evict_transition_trace[0].dir_state_tuple[0]:
                        Debug.pwarning("Directory state mismatch at ProxyDir when chaining access trace and "
                                       "evict trace")

                    # Returns a copy of the chained transition, so that the access_transition can be convoluted with
                    # other evicts traces if necessary as well
                    proxy_dir_trans.add(ChainTransitions.chain_transitions(access_transition_trace[-1],
                                                                           evict_transition_trace[0]))

                    self.proxy_dir_stable_states.update((access_transition_trace[0].start_state,
                                                         evict_transition_trace[-1].final_state))
                    access_transition_trace[0].start_state.stable = True
                    evict_transition_trace[-1].final_state.stable = True

        proxy_dir_trans.update(self.basic_single_loop_transition_inheritance(set(self.proxy_dir_states.values())))

        return proxy_dir_trans

    def gen_evict_proxy_dir_trans_dict(self) -> Dict[State_v2, Dict[State_v2, List[Tuple[ProxyDirTransition]]]]:
        evict_traces_dict: Dict[State_v2, Dict[List[Tuple[Transition_v2], SystemTuple]]] = self.get_evict_trace_dict()
        return_evict_proxy_dir_trans_dict: Dict[State_v2, Dict[State_v2, List[Tuple[ProxyDirTransition]]]] = {}

        for cache_start_state in evict_traces_dict:
            return_evict_proxy_dir_trans_dict[cache_start_state] = MultiDict()
            for dir_start_state in evict_traces_dict[cache_start_state]:
                evict_proxy_dir_trans_list = []
                for evict_trace in evict_traces_dict[cache_start_state][dir_start_state]:
                    for trans_tuple, system_tuple in evict_trace.items():
                    #for trans_tuple, system_tuple in evict_traces_dict[cache_start_state][dir_start_state].items():
                        evict_proxy_dir_trans_list.append(self.cluster_proxy_dir_transitions(trans_tuple, system_tuple))
                return_evict_proxy_dir_trans_dict[cache_start_state][dir_start_state] = evict_proxy_dir_trans_list
        return return_evict_proxy_dir_trans_dict

    def gen_access_proxy_dir_trans_dict(self) -> Dict[Tuple[State_v2, State_v2], List[Tuple[ProxyDirTransition]]]:
        access_traces_dict: Dict[BaseAccess.Access, Dict[Tuple[Transition_v2], SystemTuple]] \
            = self.get_access_trace_dict()
        access_proxy_dir_trans_dict = MultiDict()

        for access in sorted(access_traces_dict, key=lambda x: str(x)):
            for access_trace in sorted(access_traces_dict[access], key=lambda x: str(x[0])):
                system_tuple = access_traces_dict[access][access_trace]
                dir_final_state = system_tuple.get_arch_machines(self.initial_arch_level.directory)[0].final_state
                final_state = self.get_cache_access_trace(system_tuple,
                                                          self.initial_arch_level).trace_trans[-1].final_state

                access_proxy_dir_trans_dict[(final_state, dir_final_state)] = \
                    self.cluster_proxy_dir_transitions(access_trace, system_tuple)
        return access_proxy_dir_trans_dict

    def get_access_trace_dict(self) -> Dict[BaseAccess.Access, Dict[Tuple[Transition_v2], SystemTuple]]:
        guard_trace_dict: Dict[BaseAccess.Access, Dict[Tuple[Transition_v2], SystemTuple]] = {}
        for guard in self.access_system_tuples:
            guard_trace_dict[guard] = self.get_traces_from_graphs(self.access_system_tuples[guard])
        return guard_trace_dict

    def get_evict_trace_dict(self) -> Dict[State_v2, Dict[State_v2, Dict[Tuple[Transition_v2], SystemTuple]]]:
        evict_trace_dict: Dict[State_v2, Dict[State_v2, Dict[Tuple[Transition_v2], SystemTuple]]] = {}
        for start_state in self.evict_system_tuples:
            evict_trace_dict[start_state] = MultiDict()
            for system_tuple in self.evict_system_tuples[start_state]:
                dir_start_state = system_tuple.get_arch_machines(self.initial_arch_level.directory)[0].start_state
                evict_trace_dict[start_state][dir_start_state] = self.get_traces_from_graphs([system_tuple])
        return evict_trace_dict

    def get_traces_from_graphs(self, system_tuples: List[SystemTuple]) -> Dict[Tuple[Transition_v2], SystemTuple]:
        trans_path_state_map: Dict[Tuple[Transition_v2], SystemTuple] = {}
        for system_tuple in system_tuples:
            trace_graph_check = ProxyCacheGraph(system_tuple, self.initial_arch_level)
            trans_trace_list = trace_graph_check.get_trans_traces()

            for trans_trace in trans_trace_list:
                new_tuple = tuple(trans_trace)
                trans_path_state_map[new_tuple] = system_tuple

        return trans_path_state_map

    def cluster_proxy_dir_transitions(self, trans_trace: Tuple[Transition_v2], system_tuple: SystemTuple) -> \
            Tuple[ProxyDirTransition]:
        # Verify that messages are unique and extract the proxy cache and dir transitions required
        proxy_dir_transitions, internal_msgs = self.unique_message_check(system_tuple)

        # Now perform clustering for cache traces, the traces with the lowest numbers of clusters win, as the lowest
        # amount of inter-leavings are required to execute the initial traces. This is the case as proxy and dir
        # cache accesses are instantaneous and atomic
        clustered_trans_traces: List[ProxyDirTransition] = []
        new_cluster: List[Transition_v2] = []
        proxy_dir_start_state = None

        for transition in trans_trace:
            if transition not in proxy_dir_transitions:
                continue
            if str(transition.guard) in internal_msgs:
                new_cluster.append(transition)
            else:
                if new_cluster:
                    new_proxy_dir_trans = self.gen_proxy_dir_transition(new_cluster, system_tuple,
                                                                        proxy_dir_start_state)
                    clustered_trans_traces.append(new_proxy_dir_trans)
                    proxy_dir_start_state = new_proxy_dir_trans.final_state

                new_cluster = [transition]

        if new_cluster:
            new_proxy_dir_trans = self.gen_proxy_dir_transition(new_cluster, system_tuple, proxy_dir_start_state)
            clustered_trans_traces.append(new_proxy_dir_trans)

        return tuple(clustered_trans_traces)

    def gen_proxy_dir_transition(self, new_cluster, system_tuple: SystemTuple, proxy_dir_start_state: ProxyDirState):
        return ProxyDirTransition(new_cluster, system_tuple,
                                  self.initial_arch_level.cache, self.initial_arch_level.directory,
                                  self.proxy_dir_states, proxy_dir_start_state)

    @staticmethod
    def get_proxy_dir_states(transitions: Set[ProxyDirTransition]) -> Set[ProxyDirState]:
        # Extract all ProxyDirStates
        proxy_dir_states: Set[ProxyDirState] = set()

        for transition in transitions:
            if isinstance(transition.start_state, ProxyDirState):
                proxy_dir_states.add(transition.start_state)
            if isinstance(transition.final_state, ProxyDirState):
                proxy_dir_states.add(transition.final_state)

        return proxy_dir_states

    # Inherit looping transitions. Loops cannot be longer than one transition. Longer loops are not supported
    #  by the SSP language, unless transient states are manually described
    @staticmethod
    def basic_single_loop_transition_inheritance(proxy_dir_states: Set[ProxyDirState]):
        # Extract all ProxyDirStates
        new_transitions: Set = set()

        for proxy_dir_state in proxy_dir_states:
            for state in [proxy_dir_state.proxy_state]:     #, proxy_dir_state.dir_state):  # For the dir state inheritance auxiliary states need to be considered
                for transition in state.state_trans:
                    if transition.start_state == transition.final_state \
                            and not isinstance(transition.guard, BaseAccess.Access):
                        new_trans = transition.copy_modify_trans(proxy_dir_state, proxy_dir_state)
                        proxy_dir_state.add_transition(new_trans)
                        new_transitions.add(new_trans)

        return new_transitions

    def cache_initial_state_event_inheritance(self) -> Set[Transition_v2]:
        # Extract all ProxyDirStates
        new_transitions: Set[Transition_v2] = set()

        for state in self.proxy_dir_stable_states:
            init_state = self.initial_arch_level.cache.init_state
            for trace_tree in self.initial_arch_level.cache.state_sub_tree_dict[init_state]:
                tree_guard = [trans.guard for trans in self.get_transitions_by_start_state(trace_tree, init_state)]
                if len(tree_guard) != 1:
                    Debug.pwarning("Unexpected number of initial guards found in tree")
                    continue
                if isinstance(tree_guard[0], Event):
                    # Check if all root and terminal nodes of event_ack tree in initial state end up in initial state
                    # again
                    tree_root_terminal_node_set = set(self.get_terminal_nodes_by_attribute(trace_tree))
                    tree_root_terminal_node_set.add(self.get_root_node_by_attribute(trace_tree))
                    Debug.perror("Unexpected terminal states for event tree in root node",
                                 len(tree_root_terminal_node_set) == 1)

                    copy_graph = CompoundStateGenNetworkx().gen_compound_states_graph(trace_tree, [state])

                    # The root and terminal nodes should remain unchanged
                    copy_root_terminal_state = self.get_root_node_by_attribute(copy_graph)
                    for transition in self.get_transitions_by_start_state(copy_graph, copy_root_terminal_state):
                        transition.start_state = state

                    for transition in self.get_transitions_by_final_state(copy_graph, copy_root_terminal_state):
                        transition.final_state = state

                    new_transitions.update(self.get_transitions_from_graph(copy_graph))

        return new_transitions

    ## This function checks if the messages being sent between the machines are unique, that means not two machines can
    #   send nor receive the same message names
    #   This function can be later replaced if the communication patterns are clear by for example consulting a model
    #   checker in the front end. At the moment the ProtoGen model checker does only check message names
    def unique_message_check(self, system_tuple: SystemTuple):

        # Get the proxy cache trace
        proxy_trans_trace = self.get_cache_access_trace(system_tuple, self.initial_arch_level)
        Debug.perror('No proxy cache trace found', proxy_trans_trace)

        # Get the directory trace
        dir_trans_trace = self.get_dir_trace(system_tuple, self.initial_arch_level)


        # Get all remote traces
        remote_out_msg = []
        remote_in_msg = []
        for trace in system_tuple.get_traces():
            if trace is not proxy_trans_trace and trace is not dir_trans_trace:
                remote_out_msg += [str(out_msg) for out_msg in trace.out_msg]
                remote_in_msg += [str(guard) for guard in trace.all_guards]

        out_msg_sets = []
        in_msg_sets = []

        # Add proxy cache messages
        out_msg_sets.append({str(out_msg) for out_msg in proxy_trans_trace.out_msg})
        in_msg_sets.append({str(guard) for guard in proxy_trans_trace.all_guards})

        # Add directory traces if cache cannot perform transaction silently
        if dir_trans_trace:
            out_msg_sets.append({str(out_msg) for out_msg in dir_trans_trace.out_msg})
            in_msg_sets.append({str(guard) for guard in dir_trans_trace.all_guards})

        # Add remote messages from remote traces
        out_msg_sets.append(set(remote_out_msg))
        in_msg_sets.append(set(remote_in_msg))

        # Check that messages are unique, so that the message sources and destinations are clear without analyzing the
        # message source and destination entries
        for set_comb in combinations(out_msg_sets, 2):
            Debug.perror('Intersection found, message names in transactions are not unique for each controller',
                         set_comb[0].intersection(set_comb[1]) == set())

        for set_comb in combinations(in_msg_sets, 2):
            Debug.perror(f'Intersection found, message names in transactions are not unique for each controller '
                         f'{set_comb[0].intersection(set_comb[1])}',
                         set_comb[0].intersection(set_comb[1]) == set())

        # Internal messages
        internal_msgs = (out_msg_sets[0].intersection(in_msg_sets[1])).union(
            out_msg_sets[1].intersection(in_msg_sets[0]))

        # Remove looping remote message transitions associated with states that have an outgoing internal message edge.
        #  The edge is immediately taken and hence the looping transition will never be executed
        pruned_trace_list = self.prune_remote_msg_wait_loops(proxy_trans_trace.trace_trans, internal_msgs)
        if dir_trans_trace:
            pruned_trace_list += self.prune_remote_msg_wait_loops(dir_trans_trace.trace_trans, internal_msgs)

        return pruned_trace_list, internal_msgs

    @staticmethod
    def prune_remote_msg_wait_loops(trace: List[Transition_v2], internal_msgs: Set[str]):
        immediate_states: List[State_v2] = []
        for trans in trace:
            if str(trans.guard) in internal_msgs:
                immediate_states.append(trans.start_state)

        pruned_trace: List[Transition_v2] = []
        for trans in trace:
            if not(trans.start_state == trans.final_state and
                   trans.start_state in immediate_states and
                   str(trans.guard) not in internal_msgs):
                pruned_trace.append(trans)
        return pruned_trace
