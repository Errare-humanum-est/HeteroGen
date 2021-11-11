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

import os

from typing import Dict, List, Union, Any
from antlr3.tree import CommonTree
from networkx import MultiDiGraph

from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.ClassMultiDict import MultiDict
from Algorithms.ControllerGeneration.NetworkxGeneral.TreeBaseNetworkx import TreeBaseNetworkx
from DataObjects.FlowDataTypes.ClassBaseAccess import Access, Evict
from DataObjects.FlowDataTypes.ClassMessage import Message
from DataObjects.FlowDataTypes.ClassEvent import EventAck

from Backend.Common.GenCondTokenTree import CondTokenTree, CondTokenNode, MsgTokenNode, \
    BaseCondTokenNode
from Backend.Common.GenPCCToBase import GenPCCToBase
from Parser.ProtoCCcomTreeFct import childsToStringList
from Debug.Graphv.ParserNetworkxGraph import ParserPCCGraph
from Debug.Monitor.ClassDebug import Debug


class UniqueNode:
    _union_type = Union[CondTokenNode, CondTokenTree, 'UniqueNode', CommonTree, State_v2]

    def __init__(self, data: Any, children: Union[_union_type, List[_union_type]] = None):
        self.data = data
        self.children: List[Union['UniqueNode', CommonTree]] = children
        if self.children and not isinstance(self.children, List):
            self.children = [self.children]
        elif not self.children:
            self.children = []

    def __str__(self):
        return str(self.data)

    # ANTLR3 conform function call
    def getChildren(self):
        return self.children


## Nested dictionary that contains all operation token sequences, sorted by State -> Guard -> Token Sequence
#
#  The clustered operation tree is converted into a dictionary, also the final states are labeled with a unique token,
#  and the conditionals are labeled with correct if else statements to correctly support languages that cannot handle
#  returns if the final state assignment is reached
#  There exists no
#  Format: (Each node is a condition graph node)
#                                        I_load_['op0 eg COND_', ...] --> S0
#                                        /
#                                       /
#   I0 --> I_['op0', 'op1', ...] --> I_load0
#                                       \
#                                        \
#                                       I_load_['op0 eg NCOND_', ...] --> E0
#
# Fork nodes are CommonTree nodes from antlr3 frontend: ['COND_', 'NCOND_', 'TRANS_', 'GUARD_', 'EVENT_ACK_']
# Fork nodes are of different types ('COND_', 'NCOND_') => CONDITIONAL

class TokenSequenceFromTree(CondTokenTree):

    # Type declarations to improve readability
    _node_union_list_type = List[Union[CommonTree, UniqueNode]]
    _guard_types = Union[Access, Evict, Message, EventAck]
    _token_sequence_dict_type = Dict[_guard_types, _node_union_list_type]

    def __init__(self, transition_tree: MultiDiGraph):
        CondTokenTree.__init__(self)

        # Get the root transition for classification purpose
        root_state = TreeBaseNetworkx.get_root_node_by_attribute(transition_tree)
        guard_trans = TreeBaseNetworkx.get_transitions_by_start_state(transition_tree, root_state)
        self.init_guard = {trans.guard for trans in guard_trans}
        Debug.perror("More than one init guard found in transition tree: "
                     + '; '.join([str(trans_guard) for trans_guard in self.init_guard]), len(self.init_guard) == 1)
        self.init_guard = list(self.init_guard)[0]

        ## Nested dictionary that contains all operation token sequences, sorted by State -> Guard -> Token Sequence
        guard_type = Union[Access, Evict, Message, EventAck]
        self.state_operation_seq_dict: Dict[State_v2, Dict[guard_type, List[Union[CommonTree, UniqueNode]]]] = {}

        cond_operation_tree = self._gen_operation_tree(transition_tree)
        self._gen_operation_token_sequence(cond_operation_tree)

    ## Convert subtree from operation to token sequence. The subtree includes all operation nodes between state nodes
    #  @param self The object pointer.
    def _gen_operation_token_sequence(self, cond_operation_tree: MultiDiGraph):
        fsm_states = {node for node in cond_operation_tree.nodes if not isinstance(node, BaseCondTokenNode)}

        for fsm_state in fsm_states:
            simple_paths = list(self._all_simple_paths_multigraph(cond_operation_tree, fsm_state, fsm_states,
                                                                  len(cond_operation_tree)+1))
            if not simple_paths:
                continue
            node_set = set()
            for simple_path in simple_paths:
                node_set.update(simple_path)
            state_sub_tree = cond_operation_tree.subgraph(node_set)
            #ParserPCCGraph.debug_process_graph(state_sub_tree, f"TokenSequence {os.path.basename(__file__)}")
            # Convert each subtree, consisting of a start_state, N final_states and N guards into new token sequences
            self._convert_subtree_to_token_sequence(state_sub_tree, fsm_state)

    def _convert_subtree_to_token_sequence(self, sub_tree: MultiDiGraph, start_state: State_v2):
        token_sequence_dict = {}
        token_sequence: List[Union[CommonTree, UniqueNode]] = []
        trans_nodes = self._sort_next_token_clusters(list(sub_tree.successors(start_state)))
        for trans_node in trans_nodes:
            guard_list: List[Union[Access, Evict, Message, EventAck]] = []
            self._successor_to_string(guard_list, token_sequence, sub_tree, [trans_node])

            Debug.perror("No operation token found", token_sequence and len(guard_list))
            Debug.perror(f"Unexpected number of guards found {guard_list}", len(guard_list) == 1)
            Debug.perror(f"Guard already exists in guard dictionary: {guard_list[0]}",
                         guard_list[0] not in token_sequence_dict)

            # FILTER TOKEN SEQUENCE FOR ENDIF BEFORE ELSE RELATED TO THE SAME CONDITION THIS IS NECESSARY AS NOT
            #  EVERY IF IS EXPECTED TO HAVE AN ELSE, ESPECIALLY WITH RESPECT TO HETEROGEN
            token_sequence = self._remove_redundant_endif(token_sequence)

            token_sequence_dict[guard_list[0]] = token_sequence

            token_sequence = []

        self.state_operation_seq_dict[start_state] = token_sequence_dict

    @staticmethod
    def _remove_redundant_endif(token_sequence_list: _node_union_list_type) -> _node_union_list_type:
        op_endif_list = []
        for operation in reversed(token_sequence_list):
            if str(operation) == GenPCCToBase.k_else:
                op_endif_list.append(''.join(childsToStringList(operation.getChildren()[0])))
            elif str(operation) == GenPCCToBase.k_endif:
                child_str = ''.join(childsToStringList(operation.getChildren()[0]))

                if child_str not in op_endif_list:
                    continue

                # Replace string with operation object
                op_endif_list.remove(child_str)
                op_endif_list.append(operation)

        if op_endif_list:
            return [operation for operation in token_sequence_list if operation not in op_endif_list]
        return token_sequence_list

    def _successor_to_string(self,
                             guard_list: List[Union[Access, Evict, Message, EventAck]],
                             token_sequence: List[Union[CommonTree, UniqueNode]],
                             sub_tree: MultiDiGraph,
                             cur_nodes: List[Union[CondTokenNode, MsgTokenNode, State_v2]]):
        # Generate the conditions
        conditions: MultiDict = MultiDict()
        for cur_node in cur_nodes:
            if isinstance(cur_node, State_v2):
                # Final state assignment of transition that was served
                token_sequence.append(UniqueNode(GenPCCToBase.k_state, cur_node))

            # If the child_node is a conditional token, then add if and elif statements
            elif isinstance(cur_node, CondTokenNode):
                child_string = ''.join(childsToStringList(cur_node.guard_token))
                conditions[child_string] = cur_node

                # Extend cond token sequence with if and else suffix
                if len(conditions[child_string]) == 1:
                    token_sequence.append(UniqueNode(GenPCCToBase.k_if, cur_node.guard_token))
                else:
                    token_sequence.append(UniqueNode(GenPCCToBase.k_else, cur_node.guard_token))

                # Add child to token list and call new successor to string function for children
                token_sequence += cur_node.token_list

                # If the current node has children add them to token sequence
                self._child_nodes_to_string(guard_list, token_sequence, sub_tree, cur_node)

                # Terminate each if with an endif, later iterate over output sequence if an endif is issued before an
                # respective else
                token_sequence.append(UniqueNode(GenPCCToBase.k_endif, cur_node.guard_token))

                Debug.perror('To many conditions nodes found for condition: ' +
                             child_string, len(conditions[child_string]) <= 2)

            elif isinstance(cur_node, MsgTokenNode):
                guard_list.append(cur_node.transition.guard)
                token_sequence += cur_node.token_list
                self._child_nodes_to_string(guard_list, token_sequence, sub_tree, cur_node)
            else:
                Debug.perror("CondTokenTreeNode type not recognized " + str(type(cur_node)))

    def _child_nodes_to_string(self,
                               guard_list: List[Union[Access, Evict, Message, EventAck]],
                               token_sequence: List[CommonTree],
                               sub_tree: MultiDiGraph,
                               cur_node: Union[CondTokenNode, MsgTokenNode, State_v2]):
        new_child_nodes = self._sort_next_token_clusters(list(sub_tree.successors(cur_node)))
        if new_child_nodes:
            self._successor_to_string(guard_list, token_sequence, sub_tree, new_child_nodes)

    ## Sort if else statements so that token with the same condition are sequential in the returned new_node_list
    #  @param self The object pointer.
    #  @param child_node_list : child_node_list: List[Union[CondTokenNode, MsgTokenNode, State_v2]] a list of child
    #  nodes that need to be sorted based on condition and (COND_, NCOND_) keywords
    @staticmethod
    def _sort_next_token_clusters(child_node_list: List[Union[CondTokenNode, MsgTokenNode, State_v2]]):
        # Extract nodes that are common tree nodes
        new_node_list = [child_node for child_node in child_node_list
                         if isinstance(child_node, (CondTokenNode, MsgTokenNode))]

        if new_node_list:
            new_node_list = sorted(new_node_list, key=lambda x: (''.join(childsToStringList(x.guard_token)),
                                                                 str(x) in CondTokenNode.cond_token_list))

        # Add the remaining nodes to the end of the node list (usually there should not be any)
        new_node_list += [child_node for child_node in child_node_list
                          if not isinstance(child_node, (CondTokenNode, MsgTokenNode))]

        return new_node_list

    ## From networkx, searches for simple paths in graph and yields them once a target state is found. Unlike default
    #  networkx implementation, the search terminates once a target state is found
    # @param self, fsm_graph: MultiDiGraph
    @staticmethod
    def _all_simple_paths_multigraph(G, source, targets: set, cutoff: int):
        visited = dict.fromkeys([source])
        stack = [(v for u, v in G.edges(source))]
        while stack:
            children = stack[-1]
            child = next(children, None)
            if child is None:
                stack.pop()
                if visited:
                    visited.popitem()
            elif len(visited) < cutoff:
                if child in visited and child != source:
                    continue
                if child in targets:
                    yield list(visited) + [child]
                visited[child] = None
                if child not in targets:
                    stack.append((v for u, v in G.edges(child)))
                else:
                    visited.popitem()
            else:  # len(visited) == cutoff:
                tmp_visited = set(visited.keys()) - {source}
                for target in targets - tmp_visited:
                    count = ([child] + list(children)).count(target)
                    for i in range(count):
                        yield list(visited) + [target]
                stack.pop()
                visited.popitem()
