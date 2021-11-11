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

import networkx as nx

from antlr3.tree import CommonTree
from networkx import DiGraph

from typing import List
from Debug.Monitor.ClassDebug import Debug

from DataObjects.ClassMultiDict import MultiDict

from Parser.NetworkxParser.TransTreeGeneration.ClassProtoTransGraphObject import ProtoTransGraphObject
from Parser.NetworkxParser.TransTreeGeneration.ClassProcessTree import ProcessProgramFlowTree

from Debug.Graphv.ParserNetworkxGraph import ParserPCCGraph
from Debug.Monitor.MakeDir import make_dir, dir_up


## ProcessTransFlowTree
#
#  Takes the ProcessProgramFlowTree and clusters single operations into ssp_transitions
#  Dependency: ProcessProgramFlowTree, ProtoTransGraphObject, CommonTree
class ProcessTransFlowTree(ProcessProgramFlowTree):

    transaction_tree_label = "Transaction_Tree_"

    def __init__(self, process_node: CommonTree, dbg_graph: bool = False):
        ProcessProgramFlowTree.__init__(self, process_node, dbg_graph)
        Debug.__init__(self)
        self.dbg_graph = dbg_graph

        self.trans_object_graph = DiGraph()

        # Change the output directory for the graph
        make_dir(self.transaction_tree_label[0:-1])

        self.transaction_label: str = None
        self.start_state_str_id: str = None

        # Update the transition label for the parsing graph output
        self.label_transaction_tree()

        # Map the trigger guard to all existing ProtoTransGraphObjects
        self.guard_start_trans_object_map: MultiDict = MultiDict()
        self.guard_end_trans_object_map: MultiDict = MultiDict()

        self.get_start_node_process_tree()
        self.gen_object_transitions()

        ParserPCCGraph.debug_process_graph(self.trans_object_graph,
                                           self.transaction_tree_label + self.transaction_label,
                                           self.dbg_graph)
        # Reset current graph directory
        dir_up()

    def gen_object_transitions(self):
        start_node = self.get_start_node_process_tree()

        final_state_str = str(start_node.getChildren()[0])
        if len(start_node.getChildren()) > 2:
            final_state_str = str(start_node.getChildren()[2])

        # Add base start node to transition graph
        graph_entry_node = ProtoTransGraphObject(None, start_node, final_state_str)
        self.trans_object_graph.add_node(graph_entry_node)
        self.guard_end_trans_object_map[start_node] = graph_entry_node

        # Find next node tree
        self.gen_next_transition(start_node, final_state_str)

    def gen_next_transition(self, start_node: CommonTree, final_state_str: str):
        terminal_nodes = self.get_next_terminals_process_tree(start_node)
        terminal_node_final_state_dict = self.get_paths(start_node, terminal_nodes, final_state_str)
        for terminal_node in terminal_node_final_state_dict:
            # Iterate over multidict
            for final_state_entry in terminal_node_final_state_dict[terminal_node]:
                self.gen_next_transition(terminal_node, final_state_entry)

    def get_paths(self, start_node: CommonTree, terminal_nodes: List[CommonTree], prev_final_state_str: str) -> \
            MultiDict:
        final_state_dict: MultiDict = MultiDict()
        for terminal_node in terminal_nodes:
            paths: List[List[CommonTree]] = list(nx.all_simple_paths(self.process_tree, start_node, terminal_node))
            for path in paths:

                # Avoid concurrent paths that have eventually a common terminal node, but other guards exist in the path
                if self.k_guard in [str(pcc_object) for pcc_object in path[1:-1]]:
                    continue
                if self.k_event_ack in [str(pcc_object) for pcc_object in path[1:-1]]:
                    continue

                # Terminal node
                new_node_path = path
                next_guard = None

                # If non terminal node, then shorten path and set next guard to last path element
                if str(path[-1]) == self.k_guard or str(path[-1]) == self.k_event_ack:
                    new_node_path = path[0:-1]
                    next_guard = path[-1]

                next_final_state = self.check_final_state_assignment(new_node_path, prev_final_state_str)
                final_state_dict[terminal_node] = next_final_state

                new_object = self.find_equivalent_trans_object(ProtoTransGraphObject(new_node_path,
                                                                                     next_guard,
                                                                                     next_final_state))

                self.transition_graph_add_node(new_object)

        return final_state_dict

    def find_equivalent_trans_object(self, new_object: ProtoTransGraphObject) -> ProtoTransGraphObject:
        if new_object.start_guard in self.guard_start_trans_object_map:
            for ref_object in self.guard_start_trans_object_map[new_object.start_guard]:
                if hash(ref_object) == hash(new_object):
                    if new_object.next_guard:
                        for next_guard in new_object.next_guard:
                            ref_object.update_next_guard(next_guard)
                            if (next_guard not in self.guard_end_trans_object_map or
                                    ref_object not in self.guard_end_trans_object_map[next_guard]):
                                self.guard_end_trans_object_map[next_guard] = ref_object
                    return ref_object
        else:
            # Register new_graph_node, next guard so it can be found by possible children
            if new_object.next_guard:
                for next_guard in new_object.next_guard:
                    self.guard_end_trans_object_map[next_guard] = new_object

            # Add the node to the start graph
            self.guard_start_trans_object_map[new_object.start_guard] = new_object
        return new_object

    def check_final_state_assignment(self, path: List[CommonTree], prev_final_state_str: str):
        next_final_state_assignment = None
        for pcc_object in path:
            if str(pcc_object) == self.k_assign and str(pcc_object.getChildren()[0]) == self.k_state:
                next_final_state_assignment = str(pcc_object.getChildren()[2])

        if next_final_state_assignment:
            return next_final_state_assignment
        return prev_final_state_str

    def transition_graph_add_node(self, new_graph_node: ProtoTransGraphObject):
        prev_nodes = self.guard_end_trans_object_map[new_graph_node.start_guard]

        # Append new_graph_node to parent node
        for prev_node in prev_nodes:
            self.trans_object_graph.add_edge(prev_node, new_graph_node)

        # Register new_graph_node, next guard so it can be found by possible children
        if new_graph_node.next_guard:
            for next_guard in new_graph_node.next_guard:
                self.guard_end_trans_object_map[next_guard] = new_graph_node

        # Add the node to the start graph
        self.guard_start_trans_object_map[new_graph_node.start_guard] = new_graph_node

    def get_start_node_process_tree(self) -> CommonTree:
        start_nodes = list((node for node, in_degree in self.process_tree.in_degree() if in_degree == 0))
        self.perror("To many start nodes in process tree", len(start_nodes) == 1)
        return start_nodes[0]

    def get_next_terminals_process_tree(self, cur_node: CommonTree) -> List[CommonTree]:
        terminal_node_list = []
        self.search_terminal_nodes_process_tree([cur_node], terminal_node_list)
        # Create set to avoid duplicates due to alternative paths
        return list(set(terminal_node_list))

    # Tree depth first search
    def search_terminal_nodes_process_tree(self,
                                           cur_nodes: List[CommonTree],
                                           terminal_node_list: List[CommonTree]):
        for cur_node in cur_nodes:
            # Create set to avoid duplicates due to alternative paths
            successor_nodes = list(set(self.process_tree.successors(cur_node)))

            non_terminal_nodes = []
            for successor_node in successor_nodes:

                if not (str(successor_node) == self.k_guard
                        or str(successor_node) == self.k_event_ack
                        or self.terminal in self.process_tree.nodes[successor_node]):
                    non_terminal_nodes.append(successor_node)
                else:
                    terminal_node_list.append(successor_node)

            self.search_terminal_nodes_process_tree(non_terminal_nodes, terminal_node_list)

    def label_transaction_tree(self):
        start_node = self.get_start_node_process_tree()
        self.start_state_str_id = str(start_node.getChildren()[0])
        self.transaction_label = "".join([str(pcc_object) for pcc_object in start_node.getChildren()])
