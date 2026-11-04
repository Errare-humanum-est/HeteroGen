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
from typing import Dict, Set, List, Tuple, Callable
from collections import OrderedDict

from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.ClassCluster import Cluster
from DataObjects.ClassMultiDict import MultiDict
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from networkx import DiGraph

from Parser.ParserDataTypes.ClassBaseNetwork import BaseMessage
from Backend.SLICC.ModularSLICC import SLICCTokens
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from Backend.SLICC.ModularSLICC.common import Util
from Backend.SLICC.ModularSLICC.common.GenPCCToSLICC import GenPCCToSLICC
from Backend.SLICC.ModularSLICC.common.GenSLICCTree import GenSLICCTree, UniqueNode


# TODO this class should probably be re-written to not be fully static so as to reduce the number of arguments
# being passed around... Keeping it like this for now to remain consistent with the rest of the code base
class GenMachineInPorts:
    template_file = "in_port.sm"

    @staticmethod
    def gen_machine_in_ports(
            temp_h: TemplateHandler,
            cluster: Cluster,
            arch: FlatArchitecture,
            in_ports: 'OrderedDict[str, str]',
            out_ports: 'OrderedDict[str, str]',
            main_mem_accesses: Dict[Tuple[str, str], DiGraph] = None,
    ) -> str:
        if main_mem_accesses is None:
            main_mem_accesses = {}
        nets = []
        for net_name, in_port in in_ports.items():
            nets.append(
                GenMachineInPorts._gen_in_port(
                    temp_h, net_name, in_port, cluster, arch, out_ports, main_mem_accesses))
        return temp_h.nl.join(nets)

    @staticmethod
    def _gen_in_port(
            temp_h: TemplateHandler,
            net_name: str,
            port_name: str,
            cluster: Cluster,
            arch: FlatArchitecture,
            out_ports: 'OrderedDict[str, str]',
            main_mem_accesses: Dict[Tuple[str, str], DiGraph],
    ) -> str:
        # This is *extremely* TODO/WIP
        # For now, let's try just generating the behaviour for every possible
        state_strs = []
        first = True
        slicc_tree_gen = GenSLICCTree(cluster, arch, port_name, out_ports, allow_port_popping=True)

        transitions_by_state = MultiDict()
        for transition in arch.get_architecture_transitions():
            # Nicolai, if you ever read this, overriding the "=" operator like this is very nasty lol
            # At first glance you'd hardly guess that it appends the transition...
            transitions_by_state[transition.start_state] = transition

        for state in sorted(transitions_by_state, key=lambda s: str(s)):
            transitions_by_guard = MultiDict()
            for transition in transitions_by_state.get(state, []):
                if isinstance(transition.guard, BaseMessage) \
                        and str(transition.guard) in arch.global_arch.network.base_message_dict:
                    transitions_by_guard[str(transition.guard)] = transition

            op_string = ""
            first_guard = True
            for guard in sorted(transitions_by_guard):
                prefix = f"if ({SLICCTokens.k_in_msg}.Type == CoherenceMessageType:{guard}) {{{temp_h.nl}"
                if not first_guard:
                    prefix = f"{temp_h.nl}{temp_h.tab}}} else {prefix}"
                prefix = temp_h.tab + prefix

                slicc_tree = slicc_tree_gen.gen_operation_tree_from_trans(transitions_by_guard[guard])
                test = temp_h.add_tabs(slicc_tree_gen.tree_to_str(slicc_tree), 2)

                #if Util.must_access_memory(arch):
                #    GenMachineInPorts.replace_mem_ops(temp_h, arch, cluster, slicc_tree, Util.get_active_cache_line(arch),
                #                                      transitions_by_guard[guard], main_mem_accesses, port_name)
                op = temp_h.add_tabs(slicc_tree_gen.tree_to_str(slicc_tree), 2)
                op_string += prefix + op
                first_guard = False

            if op_string:
                op_string += f"{temp_h.nl}{temp_h.tab}}} else {{{temp_h.nl}{temp_h.tab * 2}" \
                             f"{Util.gen_stall_str(temp_h, arch, port_name)}{temp_h.nl}{temp_h.tab}}}"
            else:
                # Have not generated a body for this clause as there are no expected transitions
                op_string = f"{temp_h.tab}{Util.gen_stall_str(temp_h, arch, port_name)}"

            prefix_str = f"if (st == State:{str(state)}) {{"
            body_str = f"{temp_h.nl}{op_string}{temp_h.nl}}}"
            if first:
                state_str = temp_h.add_tabs(prefix_str + body_str, 3)
                first = False
            else:
                # If we are not first then we need to prefix with an "else",
                # plus we don't want to add tabs to the first line as it will be merged
                # with the previous one (e.g. to gen_make "} else if")
                state_str = " else " + prefix_str + temp_h.add_tabs(body_str, 3)

            state_strs.append(state_str)

        else_body = temp_h.add_tabs(f"{temp_h.tab}{Util.gen_stall_str(temp_h, arch, port_name)}{temp_h.nl}}}",
                                    3)
        state_strs.append(f" else {{{temp_h.nl}{else_body}")

        return temp_h.string_repl_keys(temp_h.open_template(GenMachineInPorts.template_file),
                                       [port_name,
                                        "CoherenceMessage",
                                        net_name,
                                        "".join(state_strs),
                                        " getEntry(LineAddress)," if arch.machine.check_cache() else "",
                                        ]) \
               + temp_h.nl

    @staticmethod
    def find_mem_access_subtree_roots(operation_tree: DiGraph, is_access: Callable[[object], bool]) \
            -> List[Tuple[object, str]]:

        def populate_roots_list(node: object, roots_list: List[object], last_branch_node: object):
            pre_node = list(operation_tree.predecessors(node))
            assert len(pre_node) == 1
            pre_node = pre_node[0]

            if str(pre_node) == SLICCTokens.t_COND or str(pre_node) == SLICCTokens.t_NCOND \
                    or str(pre_node) == SLICCTokens.t_ELSE:
                last_branch_node = node
            if is_access(node):
                roots_list.append(node)
            for child_node in operation_tree.successors(node):
                populate_roots_list(child_node, roots_list, last_branch_node)

        roots = []
        base_node = [node for node, in_degree in operation_tree.in_degree(operation_tree.nodes) if in_degree == 0]
        assert len(base_node) == 1
        base_node = base_node[0]
        for child in operation_tree.successors(base_node):
            populate_roots_list(child, roots, child)

        return roots

    @staticmethod
    def pop_subtree_at_node(operation_tree: DiGraph, first_node: object) -> Tuple[DiGraph, Set[object]]:
        new_tree = DiGraph()

        # Due to the way the parser works, GenSLICCTree will effectively ignore the first
        # node in the tree; in this case it is important that the first_node is actually
        # taken into account, hence let's insert a dummy "base node" to the tree.
        base_node = UniqueNode(len(operation_tree))
        new_tree.add_node(base_node)
        new_tree.add_node(first_node, op_str=operation_tree.nodes[first_node]['op_str'])
        new_tree.add_edge(base_node, first_node)
        nodes_to_traverse = [first_node]
        nodes_to_remove = {first_node}
        while nodes_to_traverse:
            node = nodes_to_traverse.pop(0)
            children = list(operation_tree.successors(node))
            for child in children:
                new_tree.add_node(child, op_str=operation_tree.nodes[child]['op_str'])
                new_tree.add_edge(node, child)
            nodes_to_traverse.extend(children)
            nodes_to_remove.update(children)

        return new_tree, nodes_to_remove

    @staticmethod
    def replace_mem_ops(
            temp_h: TemplateHandler,
            arch: FlatArchitecture,
            cluster: Cluster,
            operation_tree: DiGraph,
            cache_line: str,
            transitions: [Transition_v2],
            main_mem_accesses: Dict[Tuple[str, str], DiGraph],
            in_port: str,
    ) -> None:

        start_state = str(transitions[0].start_state)
        guard = str(transitions[0].guard)
        assert all([str(trans.start_state) == start_state for trans in transitions]), \
            "Transitions did not all start in the same state"

        mem_read_branches = GenMachineInPorts.find_mem_access_subtree_roots(
            operation_tree,
            lambda n: f":= getEntry(LineAddress).{cache_line}" in operation_tree.nodes[n]['op_str']
        )
        mem_write_branches = GenMachineInPorts.find_mem_access_subtree_roots(
            operation_tree,
            lambda n: f"getEntry(LineAddress).{cache_line} :=" in operation_tree.nodes[n]['op_str']
        )
        assert all([node not in mem_write_branches for node in mem_read_branches]) \
            and all([node not in mem_read_branches for node in mem_write_branches]), \
            "Found overlapping main mem read and write branches"
        mem_access_nodes = [(node, "MEMORY_READ") for node in mem_read_branches] \
                           + [(node, "MEMORY_WB") for node in mem_write_branches]

        nodes_to_remove = set()

        for idx, (access_node, access_type) in enumerate(mem_access_nodes):
            predecessors = operation_tree.predecessors(access_node)
            mem_trans_state_name = f"{start_state}_{guard}_MEM_{idx}"
            trans_op_tree, popped_nodes = GenMachineInPorts.pop_subtree_at_node(operation_tree, access_node)
            nodes_to_remove.update(popped_nodes)
            # Also gen_make sure to pop the memqueue at the end of this new operation tree
            end_nodes = [node for node, out_degree in trans_op_tree.out_degree(trans_op_tree.nodes) if out_degree == 0]
            for node in end_nodes:
                if "trigger(Event" in trans_op_tree.nodes[node]["op_str"]:
                    trigger_str = f"memQueue_in.dequeue(clockEdge()){temp_h.end}" \
                                  f"trigger(Event:deallocTBE, LineAddress, tbe){temp_h.sem}"
                    trans_op_tree.nodes[node]["op_str"] = trigger_str  # dealloc TBE and pop mem queue instead
                    for prev in trans_op_tree.predecessors(node):
                        if "dequeue(" in trans_op_tree.nodes[prev]["op_str"]:
                            # Don't want to pop the queue in the in_port anymore, since we need the msg
                            # to stay in the queue until the deallocTBE transition has finished
                            trans_op_tree.nodes[prev]["op_str"] = ""

            main_mem_accesses[(mem_trans_state_name, access_type)] = trans_op_tree

            # Replace this transition with one invoking a memory read and setting the state
            # to our new transient one
            mem_access_str = temp_h.string_repl_keys(temp_h.open_template(f"{access_type}.sm"),
                                                     [Util.get_message_data_var(cluster)]
                                                     )
            mem_access_node = UniqueNode(mem_trans_state_name + mem_access_str)
            operation_tree.add_node(mem_access_node, op_str=mem_access_str)
            for node in predecessors:
                operation_tree.add_edge(node, mem_access_node)
            final_state_str = GenPCCToSLICC.gen_final_state(temp_h, mem_trans_state_name, arch)
            final_state_node = UniqueNode(mem_trans_state_name + final_state_str)
            operation_tree.add_node(final_state_node, op_str=final_state_str)
            operation_tree.add_edge(mem_access_node, final_state_node)
            # Let's not forget to pop the request too...
            pop_str = GenPCCToSLICC.gen_pop_net(temp_h, in_port)
            pop_node = UniqueNode(str(final_state_node) + pop_str)
            operation_tree.add_node(pop_node, op_str=pop_str)
            operation_tree.add_edge(final_state_node, pop_node)
            # and gen_make sure we progress..
            progress_str = Util.gen_progress_str(temp_h, arch)
            progress_node = UniqueNode(str(final_state_node) + progress_str)
            # Also add a dummy event to gen_make sure the simulation makes progress
            operation_tree.add_node(progress_node, op_str=progress_str)
            operation_tree.add_edge(pop_node, progress_node)

        # Only once all the subtrees have been extracted can we safely remove the copied nodes,
        # since the nodes may re-appear in several subtrees
        operation_tree.remove_nodes_from(nodes_to_remove)
