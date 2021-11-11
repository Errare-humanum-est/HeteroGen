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
import os
import networkx as nx

from antlr3.tree import CommonTree
from networkx import DiGraph

from typing import List

from Debug.Monitor.ClassDebug import Debug

from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from Debug.Graphv.ParserNetworkxGraph import ParserPCCGraph
from Debug.Monitor.MakeDir import make_dir, dir_up


## ProcessProgramFlowTree
#
#  Analyzes commontree tokens and generates possible program flows as a tree
#  Dependency: ProtoParserBase, Debug
class ProcessProgramFlowTree(ProtoParserBase, Debug):

    token_tree_label = "Token_Tree_"

    def __init__(self, process_tree: CommonTree, dbg_graph: bool = False):
        Debug.__init__(self, True)
        self.dbg_graph: bool = dbg_graph

        #self.dbg_graph: bool = True

        self.process_tree: DiGraph = DiGraph()

        # Change the output directory for the graph
        make_dir(self.token_tree_label[0:-1])

        self.gen_process_tree(process_tree)

        # Reset current graph directory
        dir_up()

    # Create new process root
    def gen_process_tree(self, process_node: CommonTree):
        transaction_base_node = process_node.getChildren()[0]
        self.perror("Process is missing transaction declaration", transaction_base_node)
        self.process_tree.add_node(transaction_base_node)

        self._gen_process_tree(process_node, transaction_base_node)

        self.perror("Parsed input process is not acyclic graph", nx.is_directed_acyclic_graph(self.process_tree))

        ParserPCCGraph.debug_process_graph(self.process_tree,
                                           self.token_tree_label +
                                           ", ".join(list((str(pcc_object)
                                                           for pcc_object in transaction_base_node.getChildren()))),
                                           self.dbg_graph
                                           )

    # Populate new process tree with common tree objects, handle sequential concurrent description
    def _gen_process_tree(self, sub_arch_tree: CommonTree, start_node: CommonTree):
        for arch_node in sub_arch_tree.getChildren():
            # Skip the first node, because it is already assigned
            if arch_node == start_node:
                continue

            terminal_nodes = self.find_terminal_nodes(start_node)

            if not terminal_nodes and str(arch_node) not in self.ProcessTreeEnd:
                self.pwarning("Following operation seems to have no effect: " + arch_node.toStringTree())
            for cur_node in terminal_nodes:
                if str(arch_node) in self.ProcessTree:
                    # IFELSE_, AWAIT_, BREAK_ nodes lead to process tree fork, terminal state and must be handled
                    # separately
                    method_fct = self.ProcessTree[str(arch_node)]
                    method = getattr(self, method_fct, lambda: '__UnknownNode__')
                    method(arch_node, cur_node)
                else:
                    self.process_tree.add_edge(cur_node, arch_node)

    # Fork program flows
    def _program_flow_fork(self, arch_node: CommonTree, cur_node: CommonTree):
        # The cur_node is IFELSE_/ AWAIT_ and the children are IF_/ WHEN_
        for child_node in arch_node.getChildren():
            entry_node = child_node.getChildren()[0]

            # If an alternative control flow has already generated subsequent path, dont generate it again
            if entry_node in self.process_tree.nodes:
                self.process_tree.add_edge(cur_node, entry_node)
                continue

            self.process_tree.add_edge(cur_node, entry_node)
            self._gen_process_tree(child_node, entry_node)

    def _program_flow_end(self, arch_node: CommonTree, cur_node: CommonTree):
        self.process_tree.add_edge(cur_node, arch_node)
        self.process_tree.nodes[arch_node][self.terminal] = self.terminal

    # NetworkX functions
    def find_terminal_nodes(self, cur_node: CommonTree) -> List[CommonTree]:
        descendants = self.find_descendants(cur_node)
        if not descendants:
            return [cur_node]
        end_nodes = list(nx.get_node_attributes(self.process_tree, self.terminal).keys())
        terminal_nodes = list((node for node, out_degree in self.process_tree.out_degree(descendants)
                               if out_degree == 0 and node not in end_nodes))
        return terminal_nodes

    def find_descendants(self, cur_node: CommonTree) -> List[CommonTree]:
        descendants = []
        self.get_decendants([cur_node], descendants)
        # Create set to avoid duplicates due to alternative paths
        return list(set(descendants))

    # Tree depth first search
    def get_decendants(self, cur_nodes: List[CommonTree], successor_list: List[CommonTree]):
        for cur_node in cur_nodes:
            # Create set to avoid duplicates due to alternative paths
            successor_nodes = list(set(self.process_tree.successors(cur_node)))
            self.get_decendants(successor_nodes, successor_list)
            successor_list += successor_nodes
