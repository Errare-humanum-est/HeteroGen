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

from typing import List

from networkx import MultiDiGraph

from Algorithms.ControllerGeneration.NetworkxGeneral.TreeBaseNetworkx import TreeBaseNetworkx
from DataObjects.States.ClassCompoundState import CompoundState
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from Algorithms.ControllerGeneration.General.ChainTransitions import ChainTransitions

from Algorithms.ControllerGeneration.NetworkxGeneral.CompoundStateGenNetworkx import CompoundStateGenNetworkx


class CompoundGraphsNetworkx(TreeBaseNetworkx):

    def __init__(self, prefix: str = "", gdbg: bool = False):
        TreeBaseNetworkx.__init__(self)
        self.prefix = prefix
        self.gdbg = gdbg

    ## Chains up each terminal state of the first graph with the start state of the second graph provided, returning a
    #  new compound graph
    #  @param self first_graph: MultiDiGraph, second_graph: MultiDiGraph
    def compound_graphs(self, first_graph: MultiDiGraph, second_graph: MultiDiGraph) -> MultiDiGraph:
        second_root_node = self.get_root_node_by_attribute(second_graph)

        # Update the first graph names
        first_graph = CompoundStateGenNetworkx(self.prefix).gen_compound_states_graph(first_graph, [second_root_node])
        first_root_node = self.get_root_node_by_attribute(first_graph)
        first_terminal_nodes: List[CompoundState] = self.get_terminal_nodes_by_attribute(first_graph)

        new_graph_trans = self.get_transitions_from_graph(first_graph)
        remove_trans = []
        terminal_node_list = []
        for terminal_node in first_terminal_nodes:
            # Identify first transitions to be chained
            first_terminal_trans = self.get_transitions_by_final_state(first_graph, terminal_node)

            # Update second graph names
            new_second_graph = \
                CompoundStateGenNetworkx(self.prefix).gen_compound_states_graph(second_graph,
                                                                                [terminal_node.base_states[0]])
            terminal_node_list += self.get_terminal_nodes_by_attribute(new_second_graph)

            # Identify second transitions to be chained
            second_root_trans = self.get_transitions_by_start_state(new_second_graph,
                                                                    self.get_root_node_by_attribute(new_second_graph))
            # Chain the transitions up
            new_graph_trans += self.chain_graph_transitions(first_terminal_trans, second_root_trans)
            new_graph_trans += self.get_transitions_from_graph(new_second_graph)
            remove_trans += first_terminal_trans + second_root_trans

        new_graph_trans = set(new_graph_trans).difference(remove_trans)

        new_graph = self.gen_graph(list(new_graph_trans))

        # Update the root and terminal nodes for legacy purpose
        self.set_root_node_attribute(new_graph, first_root_node)
        self.set_terminal_nodes_attribute(new_graph, terminal_node_list)

        if self.gdbg:
            self.dbg_tree_graph(new_graph)

        return new_graph

    @staticmethod
    def chain_graph_transitions(start_transitions: List[Transition_v2],
                                final_transitions: List[Transition_v2]) -> List[Transition_v2]:
        chained_transitions = []
        for start_transition in start_transitions:
            for final_transition in final_transitions:
                chained_transitions.append(ChainTransitions.chain_transitions(start_transition, final_transition))

        return chained_transitions
