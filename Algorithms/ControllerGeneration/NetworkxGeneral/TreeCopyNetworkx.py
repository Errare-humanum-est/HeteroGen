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

from typing import Dict, List

from networkx import MultiDiGraph

from DataObjects.States.ClassStatev2 import State_v2
from Debug.Monitor.ClassDebug import Debug

from Algorithms.ControllerGeneration.NetworkxGeneral.TreeBaseNetworkx import TreeBaseNetworkx


class TreeCopyNetworkx(TreeBaseNetworkx, Debug):

    def __init__(self):
        TreeBaseNetworkx.__init__(self)
        Debug.__init__(self)

    ## Creates a deep copy of a graph, making a deepcopy of all ssp_transitions and updates the root node
    #  @param self, root_node: State_v2, fsm_graph: MultiDiGraph, -> MultiDiGraph
    def deepcopy_tree_modify_root(self, root_node: State_v2, fsm_graph: MultiDiGraph) -> MultiDiGraph:
        state_map_dict = {self.get_root_node_by_attribute(fsm_graph): root_node}
        return self.update_graph_states(self.deepcopy_graph(fsm_graph), state_map_dict)

    ## Creates a deep copy of a graph, making a deepcopy of all ssp_transitions
    #  @param self, fsm_graph: MultiDiGraph, -> MultiDiGraph
    def deepcopy_graph(self, fsm_graph: MultiDiGraph) -> MultiDiGraph:
        new_fsm_graph = MultiDiGraph()

        for trans in [trans.deepcopy_trans() for trans in self.get_transitions_from_graph(fsm_graph)]:
            new_fsm_graph.add_edge(trans.start_state, trans.final_state, transition=trans)

        self.set_root_node_attribute(new_fsm_graph, self.get_root_node_by_attribute(fsm_graph))
        self.set_terminal_nodes_attribute(new_fsm_graph, self.get_terminal_nodes_by_attribute(fsm_graph))

        return new_fsm_graph

    ## Updates the states in the graph according to the state dict and also updates the root and terminal nodes
    #  @param self, fsm_graph: MultiDiGraph, state_map_dict: Dict[State_v2, State_v2], -> MultiDiGraph
    def update_graph_states(self, fsm_graph: MultiDiGraph, state_map_dict: Dict[State_v2, State_v2]) -> MultiDiGraph:

        root_node = self.update_root_node(fsm_graph, state_map_dict)
        terminal_nodes = self.update_terminal_node_list(fsm_graph, state_map_dict)

        new_fsm_graph = MultiDiGraph()

        for trans in self.get_transitions_from_graph(fsm_graph):
            if trans.start_state in state_map_dict:
                trans.start_state = state_map_dict[trans.start_state]
                # Register the transition to the state
                trans.start_state.add_transition(trans)
            if trans.final_state in state_map_dict:
                trans.final_state = state_map_dict[trans.final_state]

            new_fsm_graph.add_edge(trans.start_state, trans.final_state, transition=trans)

        self.set_root_node_attribute(new_fsm_graph, root_node)
        self.set_terminal_nodes_attribute(new_fsm_graph, terminal_nodes)

        return new_fsm_graph

    ## Returns an updated root node if the current root node is element of the passed state_map_dict
    #  @param self, fsm_graph: MultiDiGraph, state_map_dict: Dict[State_v2, State_v2], -> State_v2
    def update_root_node(self, fsm_graph: MultiDiGraph, state_map_dict: Dict[State_v2, State_v2]) -> State_v2:
        root_node = self.get_root_node_by_attribute(fsm_graph)
        if root_node in state_map_dict:
            return state_map_dict[root_node]
        return root_node

    ## Returns an updated terminal node list if a terminal node is element of the passed state_map_dict
    #  @param self, fsm_graph: MultiDiGraph, state_map_dict: Dict[State_v2, State_v2], -> List[State_v2]
    def update_terminal_node_list(self,
                                  fsm_graph: MultiDiGraph,
                                  state_mapping: Dict[State_v2, State_v2]) -> List[State_v2]:
        terminal_nodes = self.get_terminal_nodes_by_attribute(fsm_graph)
        self.perror("No terminal nodes found in graph", terminal_nodes)
        new_terminal_nodes = []
        for terminal_node in terminal_nodes:
            if terminal_node in state_mapping:
                new_terminal_nodes.append(state_mapping[terminal_node])
            else:
                new_terminal_nodes.append(terminal_node)

        return new_terminal_nodes
