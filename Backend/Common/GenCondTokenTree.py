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
#
#
from antlr3.tree import CommonTree
from typing import List

from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from Parser.ProtoCCcomTreeFct import toStringList

from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.States.ClassStatev2 import State_v2

from Algorithms.ControllerGeneration.NetworkxGeneral.TreeBaseNetworkx import TreeBaseNetworkx

from Debug.Monitor.ClassDebug import Debug

from networkx import MultiDiGraph


class BaseCondTokenNode:
    def __init__(self, start_state: State_v2, token_list: List[CommonTree], transition: Transition_v2):
        self.start_state = start_state
        self.guard_token = token_list[0]
        self.token_list = []
        if len(token_list) > 1:
            self.token_list = token_list[1:]
        self.transition = transition

    def __str__(self):
        return str(self.start_state) + '_' + str(toStringList(self.guard_token))

    def __hash__(self):
        return hash((str(self.start_state), str(toStringList(self.guard_token))))

    def eq_hash(self):
        return hash((str(self.start_state), str([str(toStringList(operation)) for operation in self.token_list])))

    def __eq__(self, other):
        if type(self) == type(other):
            return self.eq_hash() == other.eq_hash()
        return False


class CondTokenNode(BaseCondTokenNode):
    cond_token_list = (ProtoParserBase.k_cond, ProtoParserBase.k_ncond)

    def __init__(self, start_state: State_v2, token_list: List[CommonTree], transition: Transition_v2):
        BaseCondTokenNode.__init__(self, start_state, token_list, transition)
        Debug.perror('Passed list of tokens does not start with conditional token',
                     str(token_list[0]) in self.cond_token_list)


class MsgTokenNode(BaseCondTokenNode):
    msg_token_list = (ProtoParserBase.k_trans, ProtoParserBase.k_guard, ProtoParserBase.k_event_ack)

    def __init__(self, start_state: State_v2, token_list: List[CommonTree], transition: Transition_v2):
        BaseCondTokenNode.__init__(self, start_state, token_list, transition)
        Debug.perror('Passed list of tokens does not start with conditional token',
                     str(token_list[0]) in self.msg_token_list)


## Generates a tree that clusters operations that are executed after a specific condition
#
#  A tree containing transitions is converted into a tree consisting of operations which are clustered based on the
#  condition statements that decide whether subsequent operations are executed
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
# Fork nodes are of different types ('COND_', 'NCOND_' =>
#
class CondTokenTree:

    def __init__(self):
        pass

    ## Make the operation tree that
    #  @param self The object pointer.
    def _gen_operation_tree(self, transition_tree: MultiDiGraph) -> MultiDiGraph:
        cond_operation_tree = MultiDiGraph()
        for edge in transition_tree.edges.data():
            self._gen_operation_nodes(TreeBaseNetworkx.get_transition_from_edge(edge), cond_operation_tree)

        # @DEBUG
        #ParserPCCGraph.debug_process_graph(cond_operation_tree, "TESTSYS")

        Debug.perror('Duplicated condition nodes in condition operation tree found',
                     len(cond_operation_tree.nodes) == len(set(cond_operation_tree.nodes)))

        return cond_operation_tree

    @staticmethod
    def _gen_operation_nodes(transition: Transition_v2, cond_operation_tree: MultiDiGraph):
        op_list: List[CommonTree] = []

        cond_operation_tree.add_node(transition.start_state)
        cond_operation_tree.add_node(transition.final_state)

        final_node = transition.final_state

        for operation in transition.operations[::-1]:
            op_list.append(operation)

            if str(operation) in CondTokenNode.cond_token_list + MsgTokenNode.msg_token_list:
                if str(operation) in CondTokenNode.cond_token_list:
                    op_node = CondTokenNode(transition.start_state, op_list[::-1], transition)
                else:
                    op_node = MsgTokenNode(transition.start_state, op_list[::-1], transition)
                cond_operation_tree.add_node(op_node)
                cond_operation_tree.add_edge(op_node, final_node)
                final_node = op_node
                op_list = []

        cond_operation_tree.add_edge(transition.start_state, final_node)
