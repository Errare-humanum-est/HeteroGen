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

from typing import List, Dict, Set

from networkx import MultiDiGraph

from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.ClassTrace import Trace
from DataObjects.ClassMultiDict import MultiDict


from Debug.Graphv.ProtoCCGraph import ProtoCCGraph

from Algorithms.ControllerGeneration.NetworkxGeneral.TreeBaseNetworkx import TreeBaseNetworkx
from Debug.Monitor.ClassDebug import Debug


## TreeNetworkx
#
#  Base class for all architectures, contains the graphs starting in stable states and ending in other stable states.
#  These graphs contain all transitions including looping transitions.
#  More details.
class TreeNetworkx(TreeBaseNetworkx, Debug):

    def __init__(self, dbg_enable: bool = False):
        TreeBaseNetworkx.__init__(self)
        Debug.__init__(self, dbg_enable)

        self.stable_states: List[State_v2] = []

        # List of transition trees
        self.state_sub_tree_dict: Dict[State_v2, List[MultiDiGraph]] = MultiDict()

    # Function generates traces
    def gen_tree_from_trans(self, stable_states: Set[State_v2], transitions: Set[Transition_v2]):
        # Clear trace List
        self.stable_states = stable_states
        self.state_sub_tree_dict = MultiDict()

        for stable_state in stable_states:
            sub_trace_trees = self.sub_tree_access_list(stable_state,
                                                        self.stable_states,
                                                        transitions)
            for sub_trace_tree in sub_trace_trees:
                self.add_tree_to_arch(sub_trace_tree)

        if self.dbg:
            self.dbg_sub_tree_graphs()

    ## New sub trees can be generated by other Algorithms like for example ProtoGen or HieraGen, these new sub_trees are
    # automatically added and their ssp_transitions are extracted and saved into the self.transition
    def add_tree_to_arch(self, new_sub_tree: MultiDiGraph):
        stable_state = self.get_root_node_by_attribute(new_sub_tree)
        self.state_sub_tree_dict[stable_state] = new_sub_tree

        # Do a sanity check
        trans_traces: List[List[Transition_v2]] = self.get_trans_traces(new_sub_tree, stable_state, self.stable_states)

        for trans_trace in trans_traces:
            new_trace = Trace(trans_trace)
            if new_trace.final_state not in self.stable_states or new_trace.start_state not in self.stable_states:
                Debug.pwarning("New trace start/final states do not match architecture stable states: "
                               + str(new_trace))

    ## Generates multiple graphs that are each triggered by a different single access transition
    # This is used to generate traces
    def sub_tree_access_list(self,
                             start_state: State_v2,
                             terminal_states: Set[State_v2],
                             transitions: Set[Transition_v2]) -> List[MultiDiGraph]:

        fsm_sub_graph_list: List[MultiDiGraph] = []

        for transition in transitions:

            fsm_graph = MultiDiGraph()

            if transition.start_state == start_state:

                if transition.final_state not in terminal_states:
                    fsm_graph = self.sub_tree(transition.final_state,
                                              terminal_states.union([start_state]),
                                              transitions)

                # Add the initial access ssp_transitions that triggers the sub tree
                fsm_graph.add_edge(transition.start_state, transition.final_state, transition=transition)

                # Clear root node and label new start state as root node
                self.clear_root_node_attribute(fsm_graph)

                self.set_root_node_attribute(fsm_graph, transition.start_state)

                if transition.final_state in terminal_states:
                    self.set_terminal_nodes_attribute(fsm_graph, transition.final_state)

                fsm_sub_graph_list.append(fsm_graph)

        return fsm_sub_graph_list

    def dbg_sub_tree_graphs(self):
        for state in self.state_sub_tree_dict:
            for entry in self.state_sub_tree_dict[state]:
                trans = self.get_transitions_from_graph(entry)   # Extract the ssp_transitions from the graph
                ProtoCCGraph(str(trans[0]), trans)

    ## New sub trees can be generated by other Algorithms like for example ProtoGen or HieraGen, these new sub_trees are
    # automatically added and their ssp_transitions are extracted and saved into the self.transition
    def add_sub_tree(self, new_sub_tree: MultiDiGraph):
        self.state_sub_tree_dict[self.get_root_node_by_attribute(new_sub_tree)] = new_sub_tree

    ####################################################################################################################
    # Backend functions
    ####################################################################################################################
    # This could be extracted
    def get_architecture_states(self) -> Set[State_v2]:
        state_set = set()
        for stable_state in self.state_sub_tree_dict:
            for fsm_sub_graph in self.state_sub_tree_dict[stable_state]:
                state_set.update(set(fsm_sub_graph.nodes))
        return state_set

    def get_architecture_transitions(self) -> Set[Transition_v2]:
        transition_set = set()
        for stable_state in self.state_sub_tree_dict:
            for fsm_sub_graph in self.state_sub_tree_dict[stable_state]:
                transition_set.update(self.get_transitions_from_graph(fsm_sub_graph))
        return transition_set

    # Function cross checks state declarations of tree nodes and ssp_transitions
    def get_architecture_states_verified(self):
        graph_node_state_list = self.get_architecture_states()
        transition_list = self.get_architecture_transitions()

        ref_state_set = set()
        for transition in transition_list:
            ref_state_set.add(transition.start_state)
            ref_state_set.add(transition.final_state)

        self.perror("Graph states and transition states are not equivalent, severe error in tool behaviour",
                    not set(graph_node_state_list).symmetric_difference(ref_state_set))

        return graph_node_state_list

