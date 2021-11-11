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
import networkx as nx

from DataObjects.ClassLevel import Level
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.ClassSystemTuple import SystemTuple
from Algorithms.ModelChecker.TraceChecker.TraceCheckGraph import TraceCheckGraph, TraceCheckerGraphNode

from Debug.Graphv.ParserNetworkxGraph import ParserPCCGraph


class ProxyCacheGraph(TraceCheckGraph):

    def __init__(self, system_tuple: SystemTuple, arch_level: Level, gdbg: bool = False):
        TraceCheckGraph.__init__(self, system_tuple)

        proxy_dir_trans = []

        # Prune execution graph so that if a proxy or dir transition is ready to be executed this happens immediately
        proxy_trace = system_tuple.get_arch_access_trace(arch_level.cache)
        dir_trace = system_tuple.get_arch_traces(arch_level.directory)

        if proxy_trace:
            proxy_dir_trans += proxy_trace[0].trace_trans
        if dir_trace:
            proxy_dir_trans += dir_trace[0].trace_trans

        self.prune_trace_check_graph(proxy_dir_trans, [self.initial_node])

        if gdbg:
            ParserPCCGraph.debug_process_graph(self.exec_graph, "ProxyCacheGraph: " + str(proxy_trace), gdbg)

    def prune_trace_check_graph(self, proxy_dir_trans: List[Transition_v2], node_list: List[TraceCheckerGraphNode]):
        # immediate next nodes
        for node in node_list:
            immediate_node_list: List[TraceCheckerGraphNode] = []

            successor_nodes = list(self.exec_graph.successors(node))

            for successor_node in successor_nodes:
                if successor_node.uut.cur_transition in proxy_dir_trans:
                    immediate_node_list.append(successor_node)

            # If nodes(transitions) that can be immediately taken by the proxy dir controller exist, then remove the
            # non immediate nodes(transitions)
            if immediate_node_list:
                for successor_node in successor_nodes:
                    if successor_node not in immediate_node_list:
                        self.remove_non_immediate_traces(successor_node)
                self.prune_trace_check_graph(proxy_dir_trans, immediate_node_list)
            else:
                # No immediate transition was identified so continue as usual
                self.prune_trace_check_graph(proxy_dir_trans, successor_nodes)

    def remove_non_immediate_traces(self, non_immediate_node: TraceCheckerGraphNode):
        terminal_nodes = self.get_exec_graph_terminal_nodes()
        node_paths = []
        # Register all terminal node paths
        for terminal_node in terminal_nodes:
            node_paths += nx.all_simple_paths(self.exec_graph, non_immediate_node, terminal_node)
        # Remove all terminal node paths
        for node_path in node_paths:
            self.exec_graph.remove_nodes_from(node_path)

        #ParserPCCGraph.debug_process_graph(self.exec_graph, "Dummy", True)




