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

from typing import List, Any

from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from Parser.CopyReducedCommonTree import copy_tree

from DataObjects.ClassCluster import Cluster
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2

from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Murphi.BaseConfig import BaseConfig
from Backend.Murphi.MurphiModular.General.GenPCCToMurphi_DECOM import GenPCCtoMurphi_Rev

from Debug.Monitor.ClassDebug import Debug

import networkx as nx
from networkx import DiGraph


class UniqueNode:

    def __init__(self, data: Any):
        self.data = data

    def __str__(self):
        return str(self.data)


class GenMurphiRevTree(GenPCCtoMurphi_Rev):

    def __init__(self, cluster: Cluster, arch: FlatArchitecture, config: BaseConfig, function_bool: bool):
        GenPCCtoMurphi_Rev.__init__(self, cluster, arch, config)

        self.cluster = cluster
        self.arch = arch

        # Variable determines if true is returned after the last operation has been performed
        self.function_bool = function_bool
        self.return_enable = True

    def gen_murphi_tree(self, transitions: List[Transition_v2]) -> str:
        operation_tree = self.gen_operation_tree_from_trans(transitions)
        murphi_operations = self.convert_operation_tree_to_murphi_tree(operation_tree)
        return "".join([str(murphi_operation) for murphi_operation in murphi_operations])

    ## Merge multiple ssp_transitions with same guard into sequential code
    #  @param self The object pointer.
    def gen_operation_tree_from_trans(self, transitions: List[Transition_v2]) -> DiGraph:
        guard = str(transitions[0].guard)
        operation_tree = DiGraph()

        operation_tree.add_node(guard)

        # Track all operations in a tree
        operation_list = []

        for transition in transitions:
            self.new_transition(str(transition.guard))
            cur_node = guard

            return_flag = True

            for op_ind in range(1, len(transition.operations)):

                operation = transition.operations[op_ind]
                node_attributes = nx.get_node_attributes(operation_tree, "op_str")

                # Check if the current operation is a stall
                if str(operation) == ProtoParserBase.k_stall:
                    return_flag = False
                    continue

                # Decode the operation string
                op_str = self.gen_operation(operation)

                if not op_str:
                    continue

                # Check if an identical operation already exists
                divergent_trace = True
                for child_node in operation_tree.successors(cur_node):
                    if node_attributes[child_node] == op_str:
                        divergent_trace = False
                        operation = child_node
                        break

                # If the trace does not diverge from previously observed traces continue, because the operation is
                # already element of the tree
                if not divergent_trace:
                    cur_node = operation
                    continue

                # Check if the operation is already element of the tree and the tree diverges
                if operation in operation_list and divergent_trace:
                    # The tree diverges so the operation needs to be copied to avoid that the current and the existing
                    # operations are considered identical in the tree
                    operation = copy_tree(operation)

                operation_list.append(operation)

                operation_tree.add_node(operation, op_str=op_str)
                operation_tree.add_edge(cur_node, operation)
                cur_node = operation

            # Update the final state permissions
            perm_node = UniqueNode(self.k_perm)
            op_str = self.gen_state_access_perm(transition)
            operation_tree.add_node(perm_node, op_str=op_str)
            operation_tree.add_edge(cur_node, perm_node)

            # The next state transition graph must be loop free
            op_str = self.gen_final_state(transition.final_state)
            # The next state transition graph must be loop free, so add an unique node
            final_node = UniqueNode(transition.final_state)
            operation_tree.add_node(final_node, op_str=op_str)
            operation_tree.add_edge(perm_node, final_node)

            # If return is activated add a return node with the appropriate outcome
            return_node = UniqueNode(MurphiTokens.k_return)
            if self.function_bool:
                operation_tree.add_node(return_node, op_str=self.gen_bool_return(return_flag))
            else:
                operation_tree.add_node(return_node, op_str=self.gen_return())
            operation_tree.add_edge(final_node, return_node)

        #ParserPCCGraph.debug_process_graph(operation_tree, "TESTSYS")

        return operation_tree

    def convert_operation_tree_to_murphi_tree(self, operation_tree: DiGraph) -> List[UniqueNode]:

        start_states: List = list((node for node, in_degree in operation_tree.in_degree(operation_tree.nodes)
                                   if in_degree == 0))
        self.perror("Unexpected number of start states: " + str(len(start_states)), len(start_states) == 1)
        start_state = start_states[0]

        path_list_str: List[UniqueNode] = []

        self.find_next_states(path_list_str, operation_tree, start_state, 0)

        return path_list_str

    def find_next_states(self, path_list_str: List[UniqueNode], operation_tree: DiGraph, op_node: Any, nest_depth: int):
        next_operations = list(operation_tree.successors(op_node))

        new_nest_depth = nest_depth

        # If multiple next operations exist these must be of type condition
        if len(next_operations) > 1:
            if [op for op in next_operations if not (str(op) == ProtoParserBase.k_cond
                                                     or str(op) == ProtoParserBase.k_ncond)]:
                Debug.pwarning("Operation mode has multiple children, but at least one child is not of type cond")
                #self.perror("Operation mode has multiple children, but at least one child is not of type cond")

            # Tracking of the nesting depth for string intend and endif closure
            new_nest_depth += 1

        for next_operation in next_operations:
            path_list_str.append(UniqueNode(self.add_tabs(operation_tree.nodes[next_operation]['op_str'],
                                                          nest_depth)))
            self.find_next_states(path_list_str, operation_tree, next_operation, new_nest_depth)

            # Add end if closure
            if str(next_operation) == ProtoParserBase.k_cond or str(next_operation) == ProtoParserBase.k_ncond:
                path_list_str.append(UniqueNode(self.add_tabs(self.gen_condition_end(), nest_depth)))

    def gen_bool_return(self, return_flag: bool) -> str:
        if return_flag:
            return MurphiTokens.k_return + " true" + self.end
        else:
            return MurphiTokens.k_return + " false" + self.end

    def gen_return(self) -> str:
        return MurphiTokens.k_return + self.end
