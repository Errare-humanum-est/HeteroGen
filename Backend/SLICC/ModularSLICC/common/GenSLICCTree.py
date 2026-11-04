#  Copyright (c) 2022.  Nicolai Oswald
#  Copyright (c) 2022.  University of Edinburgh
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

from typing import List, Any
from collections import OrderedDict

from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from Parser.CopyReducedCommonTree import copy_tree

from DataObjects.ClassCluster import Cluster
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2

from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from Backend.SLICC.ModularSLICC.common.GenPCCToSLICC import GenPCCToSLICC
from Backend.SLICC.ModularSLICC.common import Util

from Debug.Monitor.ClassDebug import Debug

import networkx as nx
from networkx import DiGraph


class UniqueNode:

    def __init__(self, data: Any):
        self.data = data

    def __str__(self):
        return str(self.data)


class GenSLICCTree(TemplateHandler, Debug):

    def __init__(
            self,
            cluster: Cluster,
            arch: FlatArchitecture,
            port_name: str,
            out_ports: 'OrderedDict[str, str]',
            allow_port_popping: bool = True,
            set_final_state: bool = True):
        Debug.__init__(self)

        self.cluster = cluster
        self.arch = arch
        self.port_name = port_name
        self.pcc_to_slicc = GenPCCToSLICC(cluster, arch, out_ports)
        self.allow_port_popping = allow_port_popping
        self.set_final_state = set_final_state

    def gen_slicc_tree(self, transitions: List[Transition_v2]) -> str:
        if len(transitions) < 1:
            return ""
        operation_tree = self.gen_operation_tree_from_trans(transitions)
        return self.tree_to_str(operation_tree)

    def tree_to_str(self, operation_tree: DiGraph) -> str:
        return self.nl.join([str(slicc_operation)
                             for slicc_operation
                             in self.convert_operation_tree_to_slicc_tree(operation_tree)])

    def gen_operation_tree_from_trans(self, transitions: List[Transition_v2]) -> DiGraph:
        guard = str(transitions[0].guard)
        operation_tree = DiGraph()

        operation_tree.add_node(guard)

        # Track all operations in a tree
        operation_list = []

        for transition in transitions:

            self.pcc_to_slicc.new_transition(str(transition.guard))
            cur_node = guard
            if self.set_final_state and transition.start_state.stable and not transition.final_state.stable:
                tbe_str = Util.check_tbe_valid(self, self.arch, self.port_name)
                operation_tree.add_node(tbe_str, op_str=tbe_str)
                operation_tree.add_edge(cur_node, tbe_str)
                cur_node = tbe_str

            pop_queue = self.allow_port_popping

            for op_ind in range(1, len(transition.operations)):
                operation = transition.operations[op_ind]
                node_attributes = nx.get_node_attributes(operation_tree, "op_str")

                # If the op is a stall, we shouldn't pop the queue
                if str(operation) == ProtoParserBase.k_stall:
                    pop_queue = False
                    continue

                op_str = self.pcc_to_slicc.gen_operation(operation)
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

            if self.set_final_state:
                op_str = GenPCCToSLICC.gen_final_state(self, str(transition.final_state), self.arch)
                # To avoid loops in the transition graph and to avoid redundant repetition
                # of setState calls in the case of multiple equivalent transitions,
                # the node corresponding to the setState() call must be unique
                # up to (and only up to) the current transition
                final_node = (
                    transition, transition.start_state, transition.final_state)
                operation_tree.add_node(final_node, op_str=op_str)
                operation_tree.add_edge(cur_node, final_node)
                cur_node = final_node

            # If we have now completed a transaction that was initiated with a load or store miss,
            # callback to gem5 to complete the transaction. Otherwise, if we have finished a transaction
            # to a state without any permissions (e.g. I in MSI), let's deallocate the block.
            # Otherwise, if we are moving from a transient state to a non-transient one, at least dealloc
            # the tbe.
            # TODO this will likely have to evolve in the future to more accurately determine
            # when callbacks/deallocations are needed
            access = None
            split_trans_name = str(transition.start_state).split("_")
            if "load" in split_trans_name:
                assert "store" not in split_trans_name, split_trans_name
                access = "load"
            elif "store" in split_trans_name:
                access = "store"
            # TODO get type of access in less hacky way...
            final_state_perms = [str(a.guard) for a in transition.final_state.access_hit]
            if access is not None and access in final_state_perms:
                end_state = str(transition.final_state)
                remote_event_name = Util.get_remote_hit_events_port(self.arch, self.port_name)[(access, end_state)]
                trigger_str = f"trigger(Event:{remote_event_name}, LineAddress, getEntry(LineAddress), " \
                              f"tbe){self.end}"
                trigger_node = UniqueNode((transition, transition.start_state, transition.final_state))
                operation_tree.add_node(trigger_node, op_str=trigger_str)
                operation_tree.add_edge(cur_node, trigger_node)
            elif self.arch.machine.check_cache() and transition.final_state in Util.get_invalid_states(self.arch):
                trigger_str = f"trigger(Event:dealloc{self.port_name}, LineAddress, getEntry(LineAddress), " \
                              f"tbe){self.end}"
                trigger_node = UniqueNode((transition, transition.start_state, transition.final_state, trigger_str))
                operation_tree.add_node(trigger_node, op_str=trigger_str)
                operation_tree.add_edge(cur_node, trigger_node)
            elif pop_queue:
                # If no event triggered, should pop queue and force progress with event
                pop_str = GenPCCToSLICC.gen_pop_net(self, self.port_name)
                pop_node = UniqueNode((transition, transition.start_state, transition.final_state, pop_str))
                operation_tree.add_node(pop_node, op_str=pop_str)
                operation_tree.add_edge(cur_node, pop_node)
                if transition.final_state.stable:
                    # If we are receiving a message and yet ending in a stable state, will have a TBE
                    # available which we should now deallocate
                    trigger_str = Util.gen_tbe_dealloc_str(self, self.arch)
                else:
                    trigger_str = Util.gen_progress_str(self, self.arch)
                trigger_node = UniqueNode((transition, transition.start_state, transition.final_state, trigger_str))
                operation_tree.add_node(trigger_node, op_str=trigger_str)
                operation_tree.add_edge(pop_node, trigger_node)

        root_nodes = list((node for node, in_degree in operation_tree.in_degree(operation_tree.nodes)
                                   if in_degree == 0))

        if len(root_nodes)>1:
            print("STOP")

        return operation_tree

    def convert_operation_tree_to_slicc_tree(self, operation_tree: DiGraph) -> List[UniqueNode]:

        start_states: List = list((node for node, in_degree in operation_tree.in_degree(operation_tree.nodes)
                                   if in_degree == 0))

        if len(start_states)>1:
            print("STOP")

        self.p_error("Unexpected number of start states: " + str(len(start_states)), len(start_states) == 1)
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
                #self.p_error("Operation mode has multiple children, but at least one child is not of type cond")'
                pass
            # Tracking of the nesting depth for string intend and endif closure
            new_nest_depth += 1

        first_cond = True
        for next_operation in next_operations:
            node_str = operation_tree.nodes[next_operation]['op_str']

            op_is_cond = str(next_operation) == ProtoParserBase.k_cond or str(next_operation) == ProtoParserBase.k_ncond
            if op_is_cond:
                if not first_cond:
                    node_str = "else " + node_str
                first_cond = False

            path_list_str.append(UniqueNode(self.add_tabs(node_str,
                                                          nest_depth)))
            self.find_next_states(path_list_str, operation_tree, next_operation, new_nest_depth)

            # Add end if closure
            if op_is_cond:
                path_list_str.append(UniqueNode(self.add_tabs(self.pcc_to_slicc.gen_condition_end(), nest_depth)))

