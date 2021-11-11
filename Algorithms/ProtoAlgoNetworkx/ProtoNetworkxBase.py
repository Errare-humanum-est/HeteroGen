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

from typing import Dict, List, Tuple, Set, Union

from networkx import MultiDiGraph

from DataObjects.ClassLevel import Level
from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.ClassStateSet import StateSet
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture

from Algorithms.ControllerGeneration.NetworkxGeneral.TreeCopyNetworkx import TreeCopyNetworkx
from Algorithms.ControllerGeneration.NetworkxGeneral.ConcurrencyNetworkx import ConcurrencyNetworkx

from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess
from DataObjects.FlowDataTypes.ClassEvent import Event

from Debug.Graphv.ProtoCCGraph import ProtoCCGraph
from Debug.Monitor.ClassDebug import Debug


# Generalize ProtoNetworkx even more. When a level is generated the states are assigned to state sets and convoluted
# states need to carry their original states internally so that the serialization stage can be derived at the
# ProtoNetworkx base stage. If a message can be seen as a serialization message depends on where potential remote
# messages come from, if they share the path with responses and if there is some ordering guaranteed between them and
# responses in the network. Furthermore, a response is only a potential serialization message if in no other state,
# reachable by serving multiple remote requests related to the start state, the same response can be observed. To gen_make
# responses serialization messages in case of conflict, encode them with state identifiers.
#
#
class ProtoNetworkxBase(TreeCopyNetworkx, ConcurrencyNetworkx):

    def __init__(self, level: Level, config = None, dbg_term: bool = False, gdbg: bool = False):

        TreeCopyNetworkx.__init__(self)
        ConcurrencyNetworkx.__init__(self)

        self.gdbg = gdbg

        self.level = level

        self.cache = self.level.cache
        self.directory = self.level.directory

        self.concurrency_max = True

        self.ProtoAlgorithm()

    def stable_state_trace_map(self,
                               sub_tree_dict: Dict[State_v2, List[MultiDiGraph]],
                               state_sets: Dict[State_v2, StateSet]) -> \
            Tuple[Dict[State_v2, List[MultiDiGraph]], Dict[State_v2, List[MultiDiGraph]]]:
        start_state_set_to_access_trace_list_map: Dict[State_v2, List[MultiDiGraph]] = {}
        start_state_set_to_remote_trace_list_map: Dict[State_v2, List[MultiDiGraph]] = {}
        for stable_state in state_sets:
            access_traces, remote_traces = self.classify_trees(stable_state, sub_tree_dict[stable_state])
            start_state_set_to_access_trace_list_map[stable_state] = access_traces
            start_state_set_to_remote_trace_list_map[stable_state] = remote_traces

        return start_state_set_to_access_trace_list_map, start_state_set_to_remote_trace_list_map

    def classify_trees(self, stable_state: State_v2, sub_trees: List[MultiDiGraph]) \
            -> Tuple[List[MultiDiGraph], List[MultiDiGraph]]:

        remote_trees = []
        access_trees = []

        # Classification can either be performed by analyzing initial classification of transition or
        # by simply checking whether trace has access field set...
        for sub_tree in sub_trees:
            transitions = self.get_transitions_by_start_state(sub_tree, stable_state)

            if not transitions:
                continue

            assert len(transitions) == 1, "Too many trigger ssp_transitions in sub_tree"

            if isinstance(transitions[0].guard, BaseAccess.Access_type) or isinstance(transitions[0].guard, Event):
                access_trees.append(sub_tree)
            else:
                remote_trees.append(sub_tree)

        return access_trees, remote_trees

    def ProtoAlgorithm(self):
        # Make trace trees
        start_state_set_to_access_trace_list_map, start_state_set_to_remote_trace_list_map = \
            self.stable_state_trace_map(self.cache.state_sub_tree_dict, self.cache.state_sets)

        self.gen_stalling_states(start_state_set_to_remote_trace_list_map, start_state_set_to_access_trace_list_map)

        self.update_architecture_tree_dict(self.cache,
                                           start_state_set_to_remote_trace_list_map,
                                           start_state_set_to_access_trace_list_map)

        if self.gdbg:
            ProtoCCGraph(str(self.cache), self.cache.get_architecture_transitions())

        #self.cache.dbg_sub_tree_graphs()

    def gen_stalling_states(self,
                            start_state_to_remote_graph_map: Dict[State_v2, List[MultiDiGraph]],
                            start_state_to_access_graph_map: Dict[State_v2, List[MultiDiGraph]]
                            ):

        iteration = 0

        while True and iteration < 10:

            iteration += 1
            # Create new stalling states and stalling ssp_transitions
            access_sub_tree_dict = self.stalling_states(start_state_to_remote_graph_map,
                                                        start_state_to_access_graph_map,
                                                        self.cache.state_sets)

            # If no new states are found
            if not access_sub_tree_dict:
                # Return new access graph
                return start_state_to_access_graph_map

            self.update_state_to_graph_map(start_state_to_access_graph_map, access_sub_tree_dict)

            self.pwarning("ProtoGen takes more than ten iterations to finish. "
                          "It is likely that ProtoGen is not working correctly", iteration == 10)

    def count_trans(self, state_to_graph_map: Dict[State_v2, List[MultiDiGraph]]) -> int:
        tree_trans_list = []
        for state in state_to_graph_map:
            for graph in state_to_graph_map[state]:
                tree_trans_list += self.get_transitions_from_graph(graph)

        tree_trans_list = list(set(tree_trans_list))

        return len(tree_trans_list)

    @staticmethod
    def update_state_to_graph_map(state_to_graph_map: Dict[State_v2, List[MultiDiGraph]],
                                  access_sub_tree_dict: Dict[MultiDiGraph, MultiDiGraph]):
        for state in state_to_graph_map:
            # Iterate over the trees that need to be replaced
            for replace_tree in access_sub_tree_dict:
                if replace_tree in state_to_graph_map[state]:
                    state_to_graph_map[state].remove(replace_tree)
                    state_to_graph_map[state].append(access_sub_tree_dict[replace_tree])

    @staticmethod
    def update_architecture_tree_dict(architecture: FlatArchitecture,
                                      start_state_to_remote_graph_map: Dict[State_v2, List[MultiDiGraph]],
                                      start_state_to_access_graph_map: Dict[State_v2, List[MultiDiGraph]]
                                      ):
        for state in start_state_to_remote_graph_map:
            for remote_tree in start_state_to_remote_graph_map[state]:
                start_state_to_access_graph_map[state].append(remote_tree)

        architecture.state_sub_tree_dict = start_state_to_access_graph_map

    def stalling_states(self, start_state_set_to_remote_trace_list_map: Dict[State_v2, List[MultiDiGraph]],
                        start_state_set_to_access_trace_list_map: Dict[State_v2, List[MultiDiGraph]],
                        state_sets: Dict[State_v2, StateSet]) -> Dict[MultiDiGraph, MultiDiGraph]:

        access_sub_tree_dict: Dict[MultiDiGraph, MultiDiGraph] = {}

        for stable_state in start_state_set_to_access_trace_list_map:

            access_sub_trees = start_state_set_to_access_trace_list_map[stable_state]

            # For every access trace
            for access_sub_tree in access_sub_trees:

                new_access_remote_sub_trees = []
                # Go through every state in the access trace
                for access_state in list(access_sub_tree.nodes()):

                    if access_state.stable or not access_state.start_state_set:
                        continue

                    self.perror("More than one start state set not supported yet",
                                len(access_state.start_state_set) == 1)

                    remote_sub_trees = start_state_set_to_remote_trace_list_map[
                        access_state.start_state_set[0].stable_state]

                    for remote_sub_tree in remote_sub_trees:
                        # Get final states of remote_sub_tree
                        remote_final_states = self.get_terminal_nodes_by_attribute(remote_sub_tree)

                        # Root base state and root base state set
                        remote_state = self.get_root_node_by_attribute(remote_sub_tree)
                        remote_init_transition = self.get_transitions_by_start_state(remote_sub_tree, remote_state)[0]

                        # Check if remote transition tree already exists in state
                        if (remote_init_transition.get_hash_ignore_states() in
                                [trans.get_hash_ignore_states() for trans in access_state.state_trans]):
                            continue

                        cond_ambiguity = False

                        # Snooping support, check if new transition is superset, when it comes to permissions, also
                        #  relevant if conditions for transient states have been manually defined
                        for trans in access_state.state_trans:
                            if str(remote_init_transition.guard) != str(trans.guard):
                                continue

                            remote_trans_cond_set = remote_init_transition.extract_cond_operations(
                                str(remote_init_transition.guard)).union([str(remote_init_transition.guard)])
                            access_trans_cond_set = trans.extract_cond_operations(
                                str(trans.guard)).union([str(trans.guard)])

                            # A to be inherited condition is either a subset or a superset of the already existing
                            # condition, unknown behaviour possibly definded in the SSP. So don't inherit
                            if (remote_trans_cond_set.issubset(access_trans_cond_set)
                                    or access_trans_cond_set.issubset(remote_trans_cond_set)):
                                self.pwarning("Inheritance in state: " + str(access_state) + " of transition "
                                              + str(remote_init_transition) + " not inherited as transition guard " +
                                              "is a superset of existing guards")
                                cond_ambiguity = True
                                break

                        if cond_ambiguity:
                            continue

                        # Map the old states to the new states
                        final_access_trees: Dict[State_v2, MultiDiGraph] = {}

                        # find new final states of remote transition
                        for remote_final_state in remote_final_states:
                            if remote_state not in access_sub_tree.nodes:
                                Debug.pwarning("ProtoGen: Remote final state not found in access tree, check output")
                                continue

                            # Get the access, out_msg and in_msg sequence and check whether an equivalent state in
                            # final state exists
                            access_trans_traces = self.get_trans_traces(access_sub_tree, remote_state, [access_state])

                            # Search for an equivalent state, if no equivalent state exists None is returned
                            equivalent_state = self.find_equivalent_path(access_trans_traces,
                                                                         start_state_set_to_access_trace_list_map,
                                                                         remote_final_state)

                            # If an equivalent state was found and this equivalent state is not a stable state,
                            # then continue. It must not be a stable state, since it is assumed that a request would
                            # not be required if a remote request performing a permission downgrade would grant the
                            # required permissions
                            if equivalent_state and equivalent_state not in state_sets:
                                final_access_trees[equivalent_state] = self.gen_terminal_node_tree(equivalent_state)
                                continue

                            # Get the remaining access sub tree if no equivalent state was found
                            remain_access_sub_tree = self.sub_tree(access_state,
                                                                   list(state_sets.keys()),
                                                                   self.get_transitions_from_graph(access_sub_tree))

                            # Store the remaining access sub_tree for later
                            final_access_trees[access_state] = remain_access_sub_tree

                        if not final_access_trees:
                            continue

                        # Create new remote sub_trees
                        remote_trees: List[MultiDiGraph] = self.gen_stalling_remote_graphs(access_state,
                                                                                           remote_sub_tree,
                                                                                           final_access_trees)

                        # Store the new access tree
                        new_access_remote_sub_trees.append(self.merge_access_sub_tree(access_sub_tree, remote_trees))

                if new_access_remote_sub_trees:
                    # Update access tree, required for nesting operation
                    new_concurrent_tree = self.merge_new_access_tree(new_access_remote_sub_trees,
                                                                     self.get_root_node_by_attribute(access_sub_tree))

                    access_sub_tree_dict[access_sub_tree] = new_concurrent_tree

                    #self.dbg_tree_graph(new_concurrent_tree)

        return access_sub_tree_dict

    def gen_stalling_remote_graphs(self,
                                   access_state: State_v2,
                                   remote_sub_tree: MultiDiGraph,
                                   final_access_trees: Dict[State_v2, MultiDiGraph]) -> List[MultiDiGraph]:
        # Rebuild the remote graph, updating the final states
        mod_remote_graph = self.deepcopy_tree_modify_root(access_state, remote_sub_tree)

        # Create new remote sub_trees
        remote_trees: List[MultiDiGraph] = []
        for final_access_tree in final_access_trees.values():

            # Generate the concurrency graph
            cartesian_graph = self.cartesian_product(mod_remote_graph, final_access_tree)
            # self.dbg_networkx_graph(cartesian_graph)

            # Prune the concurrency graph
            cartesian_graph = self.prune_root_access_transaction_cartesian_graph(
                cartesian_graph, mod_remote_graph, final_access_tree)
            # self.dbg_networkx_graph(cartesian_graph)

            # Generate cartesian product of graphs and update the cartesian tree
            res = self.update_stalling_tree_states(cartesian_graph)
            #self.dbg_tree_graph(res)
            remote_trees.append(res)
        return remote_trees

    def merge_access_sub_tree(self, access_sub_tree: MultiDiGraph, remote_trees: List[MultiDiGraph]) -> MultiDiGraph:
        # Create a new access sub tree transition state tree
        tree_trans_list = self.get_transitions_from_graph(access_sub_tree)
        for remote_tree in remote_trees:
            tree_trans_list += self.get_transitions_from_graph(remote_tree)

        # Filter the ssp_transitions
        tree_trans_list = list(set(tree_trans_list))

        # Create new access tree graph
        root_node = self.get_root_node_by_attribute(access_sub_tree)
        terminal_nodes = self.get_terminal_nodes_by_attribute(access_sub_tree)
        for remote_tree in remote_trees:
            [terminal_nodes.append(state) for state in self.get_terminal_nodes_by_attribute(remote_tree)
             if state not in terminal_nodes]
        new_access_tree = self.sub_tree(root_node, terminal_nodes, tree_trans_list)
        self.set_root_node_attribute(new_access_tree, root_node)

        # Store the new access tree
        return new_access_tree

    def merge_new_access_tree(self,
                              new_access_remote_sub_trees: List[MultiDiGraph],
                              root_node: State_v2) -> MultiDiGraph:
        terminal_nodes = []
        tree_trans_list = []
        for new_access_tree in new_access_remote_sub_trees:
            tree_trans_list += self.get_transitions_from_graph(new_access_tree)
            terminal_nodes += self.get_terminal_nodes_by_attribute(new_access_tree)

        # Filter the ssp_transitions
        tree_trans_list = list(set(tree_trans_list))

        return self.sub_tree(root_node, terminal_nodes, tree_trans_list)

    def find_equivalent_path(self, access_transitions_list: List[List[Transition_v2]],
                             start_state_set_to_access_trace_list_map: Dict[State_v2, List[MultiDiGraph]],
                             final_state: State_v2) -> Union[State_v2, None]:

        # Go through every state in the access_tree and check if a state is found where the access_transitions
        # of the original trace and the final_state_trace are the same
        access_msg_set = self.gen_msg_set(access_transitions_list)

        final_set_access_trees = start_state_set_to_access_trace_list_map[final_state]
        start_state = final_state

        # For every access trace
        for final_set_access_sub_tree in final_set_access_trees:
            for new_final_state in final_set_access_sub_tree.nodes():
                new_access_transitions_list = self.get_trans_traces(final_set_access_sub_tree,
                                                                    start_state, [new_final_state])
                if access_msg_set == self.gen_msg_set(new_access_transitions_list):
                    return new_final_state

        return None

    def gen_terminal_node_tree(self, terminal_state: State_v2) -> MultiDiGraph:
        terminal_state_graph = MultiDiGraph()
        terminal_state_graph.add_node(terminal_state)
        self.set_root_node_attribute(terminal_state_graph, terminal_state)
        self.set_terminal_nodes_attribute(terminal_state_graph, terminal_state)
        return terminal_state_graph

    @ staticmethod
    def gen_msg_set(access_transitions_list: List[List[Transition_v2]]) -> Set[Tuple[str, ...]]:
        msg_sets = set()
        for msg_access_transitions in access_transitions_list:
            msg_access_tuple = tuple(str(msg_access_transition.guard)
                                     for msg_access_transition in msg_access_transitions)
            msg_sets.add(msg_access_tuple)

        return msg_sets

    def find_paths_to_state(self, sub_tree: MultiDiGraph, start_state: State_v2, current_state: State_v2):
        return self.get_trans_traces(sub_tree, start_state, [current_state])




