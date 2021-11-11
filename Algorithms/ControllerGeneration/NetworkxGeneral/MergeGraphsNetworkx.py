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


from typing import List, Set

from networkx import MultiDiGraph

from Algorithms.ControllerGeneration.NetworkxGeneral.TreeBaseNetworkx import TreeBaseNetworkx
from DataObjects.States.ClassStatev2 import State_v2
from Debug.Monitor.ClassDebug import Debug


class MergeGraphsNetworkx(TreeBaseNetworkx, Debug):

    def __init__(self, gdbg: bool = False):
        TreeBaseNetworkx.__init__(self)
        Debug.__init__(self, True)
        self.gdbg = gdbg

    ## Merges multiple graphs that have the same root states to a single new graph
    #  @param self graphs: List[MultiDiGraph]
    def merge_identical_start_state_graphs(self, graphs: List[MultiDiGraph]) -> MultiDiGraph:
        graph_root_set = set()
        for graph in graphs:
            graph_root_set.add(self.get_root_node_by_attribute(graph))
        Debug.perror("Second root nodes are not identical as required for chaining of transitions",
                     len(graph_root_set) == 1)

        merge_graph = MultiDiGraph()

        root_nodes: Set[State_v2] = set()
        terminal_nodes: Set[State_v2] = set()

        for graph in graphs:
            root_nodes.add(self.get_root_node_by_attribute(graph))
            terminal_nodes.update(self.get_terminal_nodes_by_attribute(graph))
            self.add_transition_to_graph(merge_graph, self.get_transitions_from_graph(graph))

        Debug.perror("Merging of graphs impossible as root nodes of graphs don't match", len(root_nodes) == 1)

        self.set_root_node_attribute(merge_graph, root_nodes.pop())
        self.set_terminal_nodes_attribute(merge_graph, list(terminal_nodes))

        if self.gdbg:
            self.dbg_tree_graph(merge_graph)

        return merge_graph
