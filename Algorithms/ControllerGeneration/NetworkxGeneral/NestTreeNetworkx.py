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
from typing import List, Union, Tuple

from networkx import MultiDiGraph

from Algorithms.ControllerGeneration.NetworkxGeneral.TreeBaseNetworkx import TreeBaseNetworkx
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.States.ClassStatev2 import State_v2
from Algorithms.ControllerGeneration.NetworkxGeneral.CompoundGraphsNetworkx import CompoundGraphsNetworkx
from DataObjects.FlowDataTypes.ClassMessage import Message, BaseMessage
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess
from Algorithms.ControllerGeneration.General.DeferMessage.NestedDeferMessage import NestedDeferMessage
from DataObjects.Architecture.ClassBaseArchitecture import BaseArchitecture

from Debug.Monitor.ClassDebug import Debug


class NestTreeNetworkx(NestedDeferMessage, TreeBaseNetworkx):

    def __init__(self, base_arch: BaseArchitecture, gdbg: bool = False):
        self.gdbg: bool = gdbg
        NestedDeferMessage.__init__(self, base_arch)
        TreeBaseNetworkx.__init__(self)

    ## Nest two graphs, by deferring the request message and storing it as a variable
    #  @param self graphs: List[MultiDiGraph]
    def nest_graphs(self, remote_proxy_graph: MultiDiGraph, local_dir_graph: MultiDiGraph) -> MultiDiGraph:
        # Copy the graphs to avoid that the original graphs are manipulated
        remote_proxy_graph = self.copy_graph(remote_proxy_graph)
        local_dir_graph = self.copy_graph(local_dir_graph)

        remote_root = self.get_root_node_by_attribute(remote_proxy_graph)
        remote_terminal = self.get_terminal_nodes_by_attribute(remote_proxy_graph)

        dir_root = self.get_root_node_by_attribute(local_dir_graph)
        dir_terminal = self.get_terminal_nodes_by_attribute(local_dir_graph)

        # Get the guards of the graphs
        proxy_guard = self.get_graph_guard(remote_proxy_graph)
        dir_guard = self.get_graph_guard(local_dir_graph)

        self.push_defer_guard_proxy_transitions(self.get_transitions_from_graph(remote_proxy_graph),
                                                proxy_guard, dir_guard)
        self.pop_defer_guard_proxy_transitions(self.get_transitions_from_graph(local_dir_graph),
                                               dir_guard, proxy_guard)

        return CompoundGraphsNetworkx(str(dir_guard), self.gdbg).compound_graphs(remote_proxy_graph, local_dir_graph)

    def get_graph_guard(self, graph: MultiDiGraph) -> Union[BaseAccess.Access, Message, BaseMessage]:
        # Get the root node
        root_node = self.get_root_node_by_attribute(graph)
        root_transitions = self.get_transitions_by_start_state(graph, root_node)

        proxy_guard = list(set([trans.guard for trans in root_transitions]))
        Debug.perror("More than one type of transition guard found in root state. Unable to Nest Graphs",
                     len(proxy_guard) == 1)
        return proxy_guard[0]

    def add_new_root_transitions_to_graph(self, graph: MultiDiGraph, graph_node_tuple: Tuple[State_v2, List[State_v2]],
                                          root_transitions: List[Transition_v2]):
        self.add_transition_to_graph(graph, root_transitions)
        self.set_root_node_attribute(graph, graph_node_tuple[0])
        self.set_terminal_nodes_attribute(graph, graph_node_tuple[1])

    def copy_graph(self, graph: MultiDiGraph) -> MultiDiGraph:
        root_node = self.get_root_node_by_attribute(graph)
        terminal_nodes = self.get_terminal_nodes_by_attribute(graph)
        new_graph = self.gen_graph(list(trans.deepcopy_trans() for trans in self.get_transitions_from_graph(graph)))
        self.set_root_node_attribute(new_graph, root_node)
        self.set_terminal_nodes_attribute(new_graph, terminal_nodes)
        return new_graph
