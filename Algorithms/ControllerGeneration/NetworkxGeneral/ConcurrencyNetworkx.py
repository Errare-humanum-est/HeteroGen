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

from typing import Dict, Tuple, Union, List, Set

import networkx as nx
from networkx import MultiDiGraph

from DataObjects.States.ClassStatev2 import State_v2
from Deprecated.ClassTransition import Transition

from Algorithms.ControllerGeneration.NetworkxGeneral.TreeBaseNetworkx import TreeBaseNetworkx


from Debug.Monitor.ClassDebug import Debug


class ConcurrencyNetworkx(TreeBaseNetworkx, Debug):

    def __init__(self):
        TreeBaseNetworkx.__init__(self)
        Debug.__init__(self, True)
        pass

    ## Gives the complete cartesian product of two state transactions. This yields maximal possible concurrency, but
    #  comes with many unreachable states, to reduce the state space pruning can be applied.
    #  @param self first_graph: MultiDiGraph, second_graph: MultiDiGraph
    def cartesian_product(self, first_graph: MultiDiGraph, second_graph: MultiDiGraph) -> MultiDiGraph:
        root_tuple = (self.get_root_node_by_attribute(first_graph), self.get_root_node_by_attribute(second_graph))

        # Create terminal tuple list
        terminal_tuple_list = []
        for first_terminal_state in self.get_terminal_nodes_by_attribute(first_graph):
            for second_terminal_state in self.get_terminal_nodes_by_attribute(second_graph):
                terminal_tuple_list.append((first_terminal_state, second_terminal_state))

        # Create cartesian graph and clear inherited root and terminal node properties
        cartesian_graph = nx.cartesian_product(first_graph, second_graph)

        # Multiple nodes now have the root and terminal property, so remove these from all nodes in the graph
        self.clear_root_node_attribute(cartesian_graph)
        self.clear_terminal_nodes_attribute(cartesian_graph)

        # set new root and terminal nodes
        self.set_root_node_attribute(cartesian_graph, root_tuple)
        self.set_terminal_nodes_attribute(cartesian_graph, terminal_tuple_list)

        return cartesian_graph

    ## The cartesian graph must be pruned from any remaining access ssp_transitions after the remote request is being
    #  served, because by observing the remote request, the expected response from the directory changes based on the
    #  state in which the cache logically resides after serving the remote request.
    #  @param self cartesian_graph: MultiDiGraph, remote_graph: MultiDiGraph, access_graph: MultiDiGraph
    def prune_root_access_transaction_cartesian_graph(self,
                                                      cartesian_graph: MultiDiGraph,
                                                      remote_graph: MultiDiGraph,
                                                      access_graph: MultiDiGraph) -> MultiDiGraph:
        # The cartesian graph must be pruned from access ssp_transitions and the resulting children ssp_transitions
        # in the root state in which the remote invalidation is observed, because the

        remote_root: State_v2 = self.get_root_node_by_attribute(remote_graph)

        access_root: State_v2 = self.get_root_node_by_attribute(access_graph)
        access_tree_edges = list(access_graph.edges(data="transition"))

        # Preserve ssp_transitions entering a pruned edge
        for access_edge in access_tree_edges:
            start_node = (remote_root, access_edge[0])
            final_node = (remote_root, access_edge[1])
            if cartesian_graph.has_edge(start_node, final_node):
                cartesian_graph.remove_edge(start_node, final_node)

            # For each state combination remove all out going edges
            if access_edge[1] != access_root:
                out_edges = list(cartesian_graph.out_edges(final_node))
                for out_edge in out_edges:
                    cartesian_graph.remove_edge(*out_edge)

        # The states now become possible terminal states
        self.clear_terminal_nodes_attribute(cartesian_graph)
        self.find_terminal_nodes_and_set_attribute(cartesian_graph)

        return cartesian_graph

    # Function to merge the states assigned to the transition
    def update_stalling_tree_states(self, cartesian_graph: MultiDiGraph) -> MultiDiGraph:

        cartesian_root: State_v2 = self.get_root_node_by_attribute(cartesian_graph)
        cartesian_terminal_states: List[State_v2] = self.get_terminal_nodes_by_attribute(cartesian_graph)

        start_state_sequence_list = []

        fsm_graph = MultiDiGraph()

        # State tuple format (remote_state, access_state)
        state_tuples: Dict[Tuple[State_v2, State_v2], State_v2] = {}
        for (start_state_tuple, final_state_tuple, trans) in cartesian_graph.edges(data="transition"):
            start_state_sequence_list.append(str(start_state_tuple[0]) + "_XX_" + str(start_state_tuple[1]))

            # Generate the new start state
            if start_state_tuple in state_tuples:
                start_state = state_tuples[start_state_tuple]
            else:
                if start_state_tuple == cartesian_root:
                    start_state = start_state_tuple[0]
                else:
                    start_state = self.convolute_states(*start_state_tuple)
                state_tuples[start_state_tuple] = start_state

            if final_state_tuple in state_tuples:
                final_state = state_tuples[final_state_tuple]
            else:
                if final_state_tuple == cartesian_root:
                    final_state = final_state_tuple[0]
                elif final_state_tuple in cartesian_terminal_states:
                    final_state = final_state_tuple[1]
                else:
                    final_state = self.convolute_states(*final_state_tuple)
                state_tuples[final_state_tuple] = final_state

            new_trans = trans.copy_modify_trans(start_state, final_state)
            fsm_graph.add_edge(new_trans.start_state, new_trans.final_state, transition=new_trans)
            start_state.add_transitions(new_trans)

        self.clear_terminal_nodes_attribute(fsm_graph)
        self.find_terminal_nodes_and_set_attribute(fsm_graph)

        return fsm_graph

    @staticmethod
    def convolute_states(remote_state: State_v2, access_state: State_v2) -> Union[State_v2, None]:
        new_state_name = str(access_state) + "_x_" + str(remote_state)
        new_state = State_v2(new_state_name)

        # Rule, new convoluted state has start state set of remote state and final state set of original access request
        # This is the case, because while the (remote) start_state_set represents how the cache is currently seen by the
        # other caches in the system, the (access) final_state_set represents how it will be seen once its request
        # completes
        if remote_state.start_state_set:
            for state_set in set(remote_state.start_state_set):
                state_set.add_start_state(new_state)
        else:
            for state_set in set(remote_state.end_state_set):
                state_set.add_start_state(new_state)

        for end_state_set in set(access_state.end_state_set):
            end_state_set.add_end_state(new_state)

        return new_state

    @staticmethod
    def gen_msg_set(access_transitions_list: List[List[Transition]]) -> Set[Tuple[Tuple[str, str]]]:
        msg_sets = set()
        for msg_access_transitions in access_transitions_list:
            msg_access_tuple = tuple(msg_access_transition.get_msg_hash()
                                     for msg_access_transition in msg_access_transitions)
            msg_sets.add(msg_access_tuple)

        return msg_sets
