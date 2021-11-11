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

from antlr3.tree import CommonTree

from typing import Dict, List, Tuple
from Debug.Monitor.ClassDebug import Debug

from Parser.NetworkxParser.TransTreeGeneration.ClassProtoTransGraphObject import ProtoTransGraphObject
from Parser.NetworkxParser.TransTreeGeneration.ClassProtoTransObjectTree import ProcessTransFlowTree

from DataObjects.ClassBaseState import SSPState


## ProcessStateTransFlowTree
#
#  Takes the ProcessTransFlowTree and creates the start and final states as base states of the ssp_transitions
#  and assigns them to ssp_transitions
#  Dependency: ProcessTransFlowTree, ProtoTransGraphObject, SSPState
class ProcessStateTransFlowTree(ProcessTransFlowTree):

    transition_tree_label = "Transition_Tree_"

    def __init__(self, process_node: CommonTree, dbg_graph: bool = False):
        ProcessTransFlowTree.__init__(self, process_node, dbg_graph)
        Debug.__init__(self)

        self.trans_object_start_state_id_map: Dict[ProtoTransGraphObject, SSPState] = {}
        self.trans_object_final_state_id_map: Dict[ProtoTransGraphObject, SSPState] = {}

        self.start_node: SSPState = None
        self.final_nodes: Dict[str, SSPState] = {}
        self.guard_id: str = None

        # Resolve name conflicts
        self.state_names = [str(self.start_node)]

        # First concatenate ssp_transitions that have the same start and final states
        self.state_concat_depth_first_search()

    def state_concat_depth_first_search(self):
        start_trans_object = self.get_start_node_trans_graph()
        self.trans_object_start_state_id_map[start_trans_object] = SSPState("Root")
        self.start_node = SSPState(self.start_state_str_id)
        self.trans_object_final_state_id_map[start_trans_object] = self.start_node

        dfs_list: List[Tuple[ProtoTransGraphObject, Tuple[ProtoTransGraphObject]]] = []
        self.breath_first_search_trans_graph(start_trans_object, dfs_list)
        for node in dfs_list:
            self.gen_object_node_states(*node)

        # Remove the dummy root object path
        del self.trans_object_start_state_id_map[start_trans_object]
        del self.trans_object_final_state_id_map[start_trans_object]

    def gen_object_node_states(self, node: ProtoTransGraphObject, successor_nodes: Tuple[ProtoTransGraphObject]):
        # Get the first transaction sequence end_node
        prev_end_node = self.trans_object_final_state_id_map[node]

        # For all successor nodes check whether a start state has already been defined
        next_state_node_list = []
        for successor in successor_nodes:
            if successor in self.trans_object_start_state_id_map:
                next_state_node_list.append(self.trans_object_start_state_id_map[successor])

        if next_state_node_list:
            self.update_state_node_assignments(prev_end_node, next_state_node_list)

        # After all existing nodes have been updated generate new successor states if required
        for successor in successor_nodes:
            if successor not in self.trans_object_start_state_id_map:
                self.trans_object_start_state_id_map[successor] = prev_end_node
                new_end_node = self.gen_final_trans_state_node(successor, prev_end_node)
                self.trans_object_final_state_id_map[successor] = new_end_node

    def gen_final_trans_state_node(self, node: ProtoTransGraphObject, prev_end_node: SSPState) -> SSPState:
        if str(node.object_sequence[0]) == self.k_trans:
            self.guard_id = str(node.object_sequence[0].getChildren()[1])

        if not node.next_guard:
            # The node is a terminal node
            if {self.k_break, self.k_endproc}.intersection(set(str(pcc_object) for pcc_object in node.object_sequence)):
                # Check if final state node already exists
                if node.final_state_str in self.final_nodes:
                    return self.final_nodes[node.final_state_str]
                else:
                    if node.final_state_str == self.k_state:
                        # No final state was assigned, so assume that the state loops
                        new_final_node = self.start_node
                    else:
                        # Create new final state
                        new_final_node = SSPState(node.final_state_str)
                    self.final_nodes[node.final_state_str] = new_final_node
                    return new_final_node
            else:
                # Looping transition because no next_guard nor break assigning final state
                return prev_end_node
        else:
            # The node is not a terminal node, name the next node
            if str(node.object_sequence[0]) == self.k_guard or str(node.object_sequence[0]) == self.k_event_ack:
                new_node_name = str(prev_end_node) + "_" + str(node.object_sequence[0].getChildren()[0])
                return SSPState(new_node_name)
            else:
                new_node_name = str(prev_end_node) + "_" + str(node.object_sequence[0].getChildren()[1])
                return SSPState(new_node_name)

    def resolve_name_conflict(self, new_node_name: str) -> str:
        if new_node_name not in self.state_names:
            self.state_names.append(new_node_name)
            return new_node_name

        count = 0
        while True:
            gen_node_name = new_node_name + "_" + str(count)
            if gen_node_name not in self.state_names:
                self.state_names.append(gen_node_name)
                return gen_node_name
            count += 1

    # Function updates all state nodes in the dictionary
    def update_state_node_assignments(self, new_node: SSPState, old_nodes: List[SSPState]):
        for trans_object, state_node in self.trans_object_start_state_id_map.items():
            if state_node in old_nodes:
                self.trans_object_start_state_id_map[trans_object] = new_node

        for trans_object, state_node in self.trans_object_final_state_id_map.items():
            if state_node in old_nodes:
                self.trans_object_final_state_id_map[trans_object] = new_node

    def get_start_node_trans_graph(self) -> ProtoTransGraphObject:
        start_nodes = list((node for node, in_degree in self.trans_object_graph.in_degree() if in_degree == 0))
        self.perror("To many start nodes in process tree", len(start_nodes) == 1)
        return start_nodes[0]

    def get_terminal_nodes_trans_graph(self) -> List[ProtoTransGraphObject]:
        return list((node for node, out_degree in self.trans_object_graph.out_degree() if out_degree == 0))

    def breath_first_search_trans_graph(self,
                                        cur_node: ProtoTransGraphObject,
                                        dfs_list: List[Tuple[ProtoTransGraphObject, Tuple[ProtoTransGraphObject]]]):

        successors = list(self.trans_object_graph.successors(cur_node))
        new_tuple = (cur_node, tuple(successors))
        if new_tuple not in dfs_list and successors:
            dfs_list.append(new_tuple)

        for successor in successors:
            self.breath_first_search_trans_graph(successor, dfs_list)
