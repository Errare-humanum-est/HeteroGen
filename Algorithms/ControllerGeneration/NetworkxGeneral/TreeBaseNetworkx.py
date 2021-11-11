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

import collections
from typing import List, Union, Tuple, Set, Dict

import networkx as nx
from networkx import MultiDiGraph

from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.ClassMultiDict import MultiDict
from Debug.Graphv.ProtoCCGraph import ProtoCCGraph


## Documentation for a function.
#
#  More details.
class TreeBaseNetworkx:

    root = 'root'
    terminal = 'terminal'

    def __init__(self):
        pass

    ## Generates a graph from ssp_transitions, the root of the graph is the given start_state, the terminal_states are a
    #  list of given terminal_states, the passed transitions can be a superset of transitions needed. Only the
    #  transitions to construct the subtree between the start_state and terminal_states will be used
    #  @param self, start_state: State_v2, terminal_states: List[State_v2], ssp_transitions: List[Transition_v2]),
    #  -> MultiDiGraph:
    def sub_tree(self,
                 start_state: State_v2,
                 terminal_states: Set[State_v2],
                 transitions: Set[Transition_v2]) -> MultiDiGraph:

        fsm_graph = MultiDiGraph()
        trace_states = [start_state]
        trace_transitions = []

        new_trans = True

        while new_trans:

            new_trans = False

            for transition in transitions:
                if (transition.start_state in trace_states) and (transition not in trace_transitions):
                    new_trans = True
                    self.add_transition_to_graph(fsm_graph, transition)
                    if transition.final_state not in terminal_states:
                        trace_states.append(transition.final_state)
                    else:
                        self.set_terminal_nodes_attribute(fsm_graph, transition.final_state)
                    trace_transitions.append(transition)

        # Set the start_state as root node
        self.set_root_node_attribute(fsm_graph, start_state)

        return fsm_graph

    ## Make a graph from transitions. Includes all states and is cyclic
    #  @param self, transitions: Union[Transition_v2, List[Transition_v2]] -> List[Transition_v2]:
    def gen_graph(self, transitions: Union[Transition_v2, List[Transition_v2], Set[Transition_v2]]) -> MultiDiGraph:
        fsm_graph = MultiDiGraph()
        self.add_transition_to_graph(fsm_graph, transitions)
        return fsm_graph

    def prune_states_from_graph(self, fsm_graph_dict: Dict[State_v2, List[MultiDiGraph]], stable_states: List[State_v2],
                                prune_states: Set[State_v2]) -> MultiDict:
        pruned_fsm_graph_dict: MultiDict = MultiDict()
        for stable_state in stable_states:
            for fsm_graph in fsm_graph_dict[stable_state]:
                pruned: bool = False
                for prune_state in prune_states:
                    if prune_state in fsm_graph.nodes:
                        fsm_graph.remove_node(prune_state)
                        pruned = True
                if pruned:
                    traces = self.get_trans_traces(fsm_graph, stable_state, stable_states, len(fsm_graph)*2)
                    transitions = [trans for trans_list in traces for trans in trans_list]
                    if transitions:
                        pruned_fsm_graph_dict[stable_state] = self.sub_tree(stable_state, stable_states, transitions)
                        continue

                pruned_fsm_graph_dict[stable_state] = fsm_graph

        return pruned_fsm_graph_dict

    def prune_non_reachable_states_graph(self, fsm_graph: MultiDiGraph):
        root_nodes = self.get_root_node_ignore_loop(fsm_graph, False)
        while root_nodes:
            print("Non reachable states pruned: " + " ;".join([str(root_node) for root_node in root_nodes]))
            fsm_graph.remove_nodes_from(root_nodes)
            root_nodes = self.get_root_node_ignore_loop(fsm_graph, False)

    @staticmethod
    def add_transition_to_graph(graph: MultiDiGraph,
                                transitions: Union[Transition_v2, List[Transition_v2], Set[Transition_v2]]):
        if not isinstance(transitions, List) and not isinstance(transitions, Set):
            transitions = [transitions]
        for transition in transitions:
            graph.add_edge(transition.start_state, transition.final_state, transition=transition)

    ## Get all root node of tree, independent of labels and ignore looping transitions in doing so
    #  @param self, trace_tree: MultiDiGraph -> List[Transition_v2]:
    def get_root_node_ignore_loop(self, trace_tree: MultiDiGraph, single_root: bool = True) \
            -> Union[State_v2, List[State_v2]]:
        start_state_set, final_state_set = self.get_start_and_final_state_sets_from_trans_ignore_loop(
            self.get_transitions_from_graph(trace_tree))
        root_nodes = list(start_state_set.difference(final_state_set))
        if single_root:
            if not root_nodes:
                return self.get_root_node_by_attribute(trace_tree)

            assert len(root_nodes) == 1, "Unexpected number of root nodes"
            return root_nodes[0]
        return root_nodes

    @staticmethod
    def get_start_and_final_state_sets_from_trans_ignore_loop(transitions: List[Transition_v2]) -> \
            Tuple[Set[State_v2], Set[State_v2]]:
        start_state_set = set()
        final_state_set = set()
        for transition in transitions:
            if transition.start_state == transition.final_state:
                continue
            start_state_set.add(transition.start_state)
            final_state_set.add(transition.final_state)
        return start_state_set, final_state_set

    ## Returns a list holding a list of ssp_transitions that form a path between the given start_state to one of the
    #  given terminal states
    #  @param self, trace_tree: MultiDiGraph, start_state: State_v2, terminal_states: List[State_v2],
    #  ->  List[List[Union[Transition_v2, None]]]:
    def get_trans_traces(self,
                         trace_tree: MultiDiGraph,
                         start_state: State_v2,
                         terminal_states: List[State_v2],
                         cutoff: Union[int, None] = None) -> List[List[Union[Transition_v2, None]]]:
        #self.dbg_tree_graph(trace_tree)
        return list(self._all_simple_paths_edges_multigraph(trace_tree, start_state, terminal_states, cutoff))

    def get_trans_traces_no_loop(self,
                                 trace_tree: MultiDiGraph,
                                 start_state: State_v2,
                                 terminal_states: List[State_v2]) -> List[List[Union[Transition_v2, None]]]:
        return list(nx.all_simple_paths(trace_tree, start_state, terminal_states))

    ## Extract all ssp_transitions originating in start_state
    #  @param self, trace_tree: MultiDiGraph, start_state: State_v2, -> List[Transition_v2]:
    @classmethod
    def get_transitions_by_start_state(cls, trace_tree: MultiDiGraph, start_state: State_v2) -> List[Transition_v2]:
        transitions = cls.get_transitions_from_graph(trace_tree)
        return [transition for transition in transitions if transition.start_state == start_state]

    @classmethod
    def get_transitions_by_final_state(cls, trace_tree: MultiDiGraph, final_state: State_v2) -> List[Transition_v2]:
        transitions = cls.get_transitions_from_graph(trace_tree)
        return [transition for transition in transitions if transition.final_state == final_state]

    ## Assign the root node attribute self.root to a specific node in the tree
    # @param self, trace_tree: MultiDiGraph, root_node: Union[State_v2, Tuple[State_v2, State_v2]]
    def set_root_node_attribute(self, trace_tree: MultiDiGraph, root_node: Union[State_v2, Tuple[State_v2, State_v2]]):
        assert root_node in trace_tree.nodes, "Root Node not found in tree: " + str(root_node)
        trace_tree.nodes[root_node][self.root] = self.root

    ## Get the root node of a tree by searching for the node with the attribute self.root
    # @param self, trace_tree: MultiDiGraph, -> Union[Tuple[State_v2], State_v2]
    @classmethod
    def get_root_node_by_attribute(cls, trace_tree: MultiDiGraph) -> Union[Tuple[State_v2], State_v2]:
        root_nodes = nx.get_node_attributes(trace_tree, cls.root)
        assert len(root_nodes) == 1, "Unexpected number of root nodes"
        return list(root_nodes.keys())[0]

    ## Clear the root node attribute self.root from all nodes in a graph
    # @param self, trace_tree: MultiDiGraph
    def clear_root_node_attribute(self, trace_tree: MultiDiGraph):
        self.clear_nodes_attribute(trace_tree, self.root)

    ## Assign the terminal node self.terminal attribute to either a specific node or a list of nodes in the tree
    # @param self, trace_tree: MultiDiGraph, terminal_nodes: Union[List[Union[State_v2, Tuple[State_v2, State_v2]]],
    #                                                               Union[State_v2, Tuple[State_v2, State_v2]]]
    def set_terminal_nodes_attribute(self,
                                     trace_tree: MultiDiGraph,
                                     terminal_nodes: Union[List[Union[State_v2, Tuple[State_v2, State_v2]]],
                                                           Union[State_v2, Tuple[State_v2, State_v2]]]):
        for terminal_node in terminal_nodes if isinstance(terminal_nodes, list) else [terminal_nodes]:
            trace_tree.nodes[terminal_node][self.terminal] = self.terminal

    ## Get the terminal nodes of a tree by searching for the nodes with the attribute self.terminal
    # @param self, trace_tree: MultiDiGraph, -> List[State_v2]
    def get_terminal_nodes_by_attribute(self, trace_tree: MultiDiGraph) -> List[State_v2]:
        return list(nx.get_node_attributes(trace_tree, self.terminal).keys())

    ## Find all nodes without an outgoing transition in a tree and assign them the terminal node attribute.
    # This function returns all found terminal nodes
    # @param self, trace_tree: MultiDiGraph, -> List[State_v2]
    def find_terminal_nodes_and_set_attribute(self, trace_tree: MultiDiGraph) -> List[State_v2]:
        terminal_nodes = list((node for node, out_degree in trace_tree.out_degree(trace_tree.nodes) if out_degree == 0))
        for terminal_node in terminal_nodes:
            trace_tree.nodes[terminal_node][self.terminal] = self.terminal
        return terminal_nodes

    ## Clear the terminal node attribute self.terminal from all nodes in a graph
    # @param self, trace_tree: MultiDiGraph
    def clear_terminal_nodes_attribute(self, trace_tree: MultiDiGraph):
        self.clear_nodes_attribute(trace_tree, self.terminal)

    ## Clears the passed attribute associated with the passed attribute string from all nodes in a graph
    # @param self, trace_tree: MultiDiGraph, attribute: str
    @staticmethod
    def clear_nodes_attribute(trace_tree: MultiDiGraph, attribute: str):
        root_nodes = dict(trace_tree.nodes())
        for root_node in root_nodes:
            root_node_items = root_nodes[root_node]
            if attribute in root_node_items:
                del root_nodes[root_node][attribute]

    ## Clears the passed attribute associated with the passed attribute string from the specific passed node
    # @param self, trace_tree: MultiDiGraph, attribute: str
    @staticmethod
    def clear_node_attribute(trace_tree: MultiDiGraph, node: State_v2, attribute: str):
        root_nodes = dict(trace_tree.nodes())
        if node in root_nodes:
            root_node_items = root_nodes[node]
            if attribute in root_node_items:
                del root_nodes[node][attribute]

    ## Extract the ssp_transitions (assigned as attributes to the edges) from the graph
    # @param self, fsm_graph: MultiDiGraph, -> List[Transition_v2]
    @classmethod
    def get_transitions_from_graph(cls, fsm_graph: MultiDiGraph) -> List[Transition_v2]:
        return [cls.get_transition_from_edge(edge) for edge in fsm_graph.edges.data()]

    ## Returns the transition associated with the edge
    @staticmethod
    def get_transition_from_edge(edge):
        return edge[2]['transition']

    ## Remove
    # @param self, fsm_graph: MultiDiGraph, -> List[Transition_v2]
    @staticmethod
    def remove_transitions_from_graph(fsm_graph: MultiDiGraph, transitions: Union[Transition_v2, List[Transition_v2]]):
        if not isinstance(transitions, List):
            transitions = [transitions]
        for transition in transitions:
            fsm_graph.remove_edge(transition.start_state, transition.final_state, transition=transition)

    ## Debug function that extracts the ssp_transitions from the graph and calls the ProtoCCGraph class to print out a
    # @param self, fsm_graph: MultiDiGraph
    def dbg_tree_graph(self, fsm_graph: MultiDiGraph):
        trans = self.get_transitions_from_graph(fsm_graph)   # Extract the ssp_transitions from the graph
        if trans:
            ProtoCCGraph(str(trans[0]), trans)

    ## Modified private static method to include the returning of the ssp_transitions taken forming the path
    @staticmethod
    def _all_simple_paths_edges_multigraph(G: MultiDiGraph, source: State_v2, targets: List[State_v2], cutoff=None):
        targets = set(targets)
        if cutoff is None:
            #cutoff = len(G)-1
            cutoff = len(G)+1
        visited = collections.OrderedDict.fromkeys([])
        stack = [((u, v, c) for u, v, c in G.edges(source, data="transition"))]
        while stack:
            children = stack[-1]
            gen_child = next(children, None)

            if not isinstance(gen_child, tuple):
                gen_child = (gen_child, None)
            child = gen_child[1]

            # Yield condition evaluation
            if child is None:
                stack.pop()
                if len(visited):
                    visited.popitem()

            elif len(visited) < cutoff:
                # Loops must not happen multiple times, a transition that was taken must not be taken again
                if gen_child in visited:
                    continue
                # The next transition start state must equal
                if visited and gen_child[0] != list(visited)[-1][1]:
                    continue

                visited[gen_child] = gen_child[2]

                if child in targets:
                    yield [val for val in visited.values() if val]

                visited_keys = [entry[1] for entry in visited.keys()]

                if targets - set(visited_keys):
                    stack.append((u, v, c) for u, v, c in G.edges(child, data="transition"))
                else:
                    visited.popitem()
            else:  # len(visited) == cutoff:
                visited_keys = [entry[1] for entry in visited.keys()]

                for target in targets - set(visited_keys):
                    count = ([child] + [v[0] if isinstance(v, tuple) else v for v in children]).count(target)
                    for i in range(count):
                        yield [val for val in visited.values() if val]

                stack.pop()
                if len(visited):
                    visited.popitem()
