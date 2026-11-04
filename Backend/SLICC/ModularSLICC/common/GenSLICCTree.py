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
import re
from antlr3.tree import CommonTree
from Algorithms.HeteroGen.ClassHHDirArchitecture import HHDirArchitecture
from Parser.DataTypes.ClassProtoMachine import ProtoMachine


class UniqueNode:

    def __init__(self, data: Any):
        self.data = data

    def __str__(self):
        return str(self.data)

def expand_operation(operation: CommonTree) -> str:
    return str(operation) + "".join(expand_operation(op) for op in operation.getChildren())

class GenSLICCTree(TemplateHandler, Debug):

    def __init__(
            self,
            cluster: Cluster,
            arch: FlatArchitecture,
            cache: bool,
            port_name: str,
            out_ports: 'OrderedDict[str, str]',
            machine_mappings: dict[str, str],
            allow_port_popping: bool = True,
            set_final_state: bool = True):
        Debug.__init__(self)

        self.cluster = cluster
        self.cache = cache
        self.arch = arch
        self.port_name = port_name
        self.pcc_to_slicc = GenPCCToSLICC(cluster, arch, cache, out_ports, machine_mappings)
        self.allow_port_popping = allow_port_popping
        self.set_final_state = set_final_state
        self.evict_states = Util.proxy_evict_states(arch) if cache else set()

    def gen_slicc_tree(self, transitions: List[Transition_v2]) -> str:
        if len(transitions) < 1:
            return ""
        self.handler_label = f"{transitions[0].start_state} {transitions[0].guard}"
        operation_tree = self.gen_operation_tree_from_trans(transitions)
        return self.tree_to_str(operation_tree)

    @staticmethod
    def _exhaustive(conditions: List[Any]) -> bool:
        """The branches test some condition and its negation (COND x / NCOND x), so one of them is
        always taken."""
        polarities: dict = {}
        for op in conditions:
            key = "".join(expand_operation(child) for child in op.getChildren())
            polarities.setdefault(key, set()).add(str(op))
        return any(len(p) == 2 for p in polarities.values())

    def _writes_memory(self, transition: Transition_v2) -> bool:
        """The transition writes the cache line of a machine backed by main memory."""
        if not Util.must_access_memory(self.cache):
            return False
        line = Util.get_active_cache_line(self.arch)
        return any(str(op) == ProtoParserBase.k_assign and str(op.getChildren()[0]) == line
                   for op in transition.operations[1:])

    @staticmethod
    def _add_backend_node(operation_tree: DiGraph, cur_node: Any, op_str: str) -> Any:
        """Appends an operation of the back end (not of the IR transition) after `cur_node`. As for
        the IR operations, it is shared only with the traces that reach `cur_node` and do the same
        thing next. Keying the node by its string would join traces that diverged before it (e.g.
        the two branches of `if owner == src`), and each of them would then get the final states of
        all the joined traces."""
        for child_node in operation_tree.successors(cur_node):
            if operation_tree.nodes[child_node].get('op_str') == op_str:
                return child_node
        node = UniqueNode(op_str)
        operation_tree.add_node(node, op_str=op_str)
        operation_tree.add_edge(cur_node, node)
        return node

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

        # All transitions of a group share the start state and the guard. If any of them leaves a
        # stable state for a transient one, the TBE check must be the first node of every trace:
        # inserting it only for those transitions would make the traces diverge at the root and the
        # handler body would be emitted twice, once without the check.
        # A machine that accesses main memory (directory) also waits in a transient state for the
        # completion of a write-back to memory, even if the IR transition is stable -> stable
        # (GenMachineInPorts.replace_mem_ops adds that state); the TBE holds it meanwhile.
        needs_tbe = self.set_final_state and (
            (transitions[0].start_state.stable and any(not t.final_state.stable for t in transitions))
            or any(self._writes_memory(t) for t in transitions))

        for transition in transitions:

            self.pcc_to_slicc.new_transition(str(transition.guard))
            cur_node = guard

            refresh_mru = False
            if isinstance(self.arch, HHDirArchitecture):
                allocate, refresh_mru = Util.proxy_entry_alloc(self.arch, transition)
                if allocate:
                    cur_node = self._add_backend_node(operation_tree, cur_node, Util.check_cache_valid(self))


            if needs_tbe:
                cur_node = self._add_backend_node(
                    operation_tree, cur_node, Util.check_tbe_valid(self, self.cache, self.port_name))

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

            if refresh_mru:
                cur_node = self._add_backend_node(operation_tree, cur_node, "cache.setMRU(LineAddress);")

            if self.set_final_state:
                op_str = GenPCCToSLICC.gen_final_state(self, str(transition.final_state), self.cache)
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
            if not self.port_name:
                # the operations of an action (GenCacheActions): the transition that runs it completes
                continue

            final_state_perms = [str(a.access) for a in transition.final_state.access_hit if a.access]
            access = None
            # Only a cache with an access of its own completes it here (a proxy's compound states
            # grant none, and may name a virtual load of the manager and a store of the client)
            split_trans_name = str(transition.start_state).split("_") if final_state_perms else []
            if "load" in split_trans_name:
                assert "store" not in split_trans_name, split_trans_name
                access = "load"
            elif "store" in split_trans_name:
                access = "store"
            elif "ifetch" in split_trans_name:
                access = "ifetch"
            # An access of release-consistency code completed by a response, also in a state that
            # does not grant it (MESI-RC ntload in V)
            rc_completion = self.cache and (
                next((acc for acc, end in Util.rc_remote_completions(self.arch)
                      if end == str(transition.final_state)
                      and acc in str(transition.start_state).split("_")
                      and Util.access_kind(acc) in Util.access_statements(transition)), None))
            if rc_completion:
                access = rc_completion
                final_state_perms = final_state_perms + [rc_completion]

            # a directory completes no access
            if str(self.arch.machine.mach_type) == ProtoMachine.k_dir:
                access = None

            if access is not None and access in final_state_perms:
                end_state = str(transition.final_state)
                remote_event_name = Util.get_remote_hit_events_port(self.arch, self.port_name)[(access, end_state)]
                trigger_str = f"trigger(Event:{remote_event_name}, LineAddress, getEntry(LineAddress), " \
                              f"tbe){self.end}"
                trigger_node = UniqueNode((transition, transition.start_state, transition.final_state))
                operation_tree.add_node(trigger_node, op_str=trigger_str)
                operation_tree.add_edge(cur_node, trigger_node)
            elif self.cache and transition.final_state in Util.get_invalid_states(self.arch):
                eviction_state = Util.get_evict_trans_states_all(self.arch)
                if transition.start_state not in eviction_state \
                        and str(transition.start_state) not in self.evict_states:
                    trigger_str = f"trigger(Event:dealloc{self.port_name}, LineAddress, getEntry(LineAddress), " \
                              f"tbe){self.end}"
                else:
                    trigger_str = "tbe.dirty := false;\n" + \
                        f"{self.port_name}.dequeue(clockEdge());\n" + \
                        "trigger(Event:deallocTBE, LineAddress, getEntry(LineAddress), tbe);\n"
                trigger_node = UniqueNode((transition, transition.start_state, transition.final_state, trigger_str))
                operation_tree.add_node(trigger_node, op_str=trigger_str)
                operation_tree.add_edge(cur_node, trigger_node)
            elif str(transition.final_state) in self.evict_states \
                    and str(transition.start_state) not in self.evict_states:
                # The proxy's eviction request has been sent: free the entry right away, the data
                # needed until the acknowledgement stays in the TBE
                if pop_queue:
                    pop_str = GenPCCToSLICC.gen_pop_net(self, self.port_name)
                    pop_node = UniqueNode((transition, transition.start_state, transition.final_state, pop_str))
                    operation_tree.add_node(pop_node, op_str=pop_str)
                    operation_tree.add_edge(cur_node, pop_node)
                    cur_node = pop_node
                trigger_str = Util.gen_silent_evict(self)
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
                    trigger_str = Util.gen_tbe_dealloc_str(self, self.cache)
                else:
                    trigger_str = Util.gen_progress_str(self, self.cache)
                trigger_node = UniqueNode((transition, transition.start_state, transition.final_state, trigger_str))
                operation_tree.add_node(trigger_node, op_str=trigger_str)
                operation_tree.add_edge(pop_node, trigger_node)

        return operation_tree

    def convert_operation_tree_to_slicc_tree(self, operation_tree: DiGraph) -> List[UniqueNode]:

        start_states: List = list((node for node, in_degree in operation_tree.in_degree(operation_tree.nodes)
                                   if in_degree == 0))
        start_state = start_states[0]

        path_list_str: List[UniqueNode] = []

        self.find_next_states(path_list_str, operation_tree, start_state, 0)

        return path_list_str

    _ASSIGN_RE = re.compile(r"^\s*([\w.()]+)\s*:=\s*([^;]+);\s*$")
    _EQ_RE = re.compile(r"^\s*if \((.+?)\s*==\s*(.+?)\) \{\s*$")

    def _decided(self, cond_str: str, assigned: dict) -> bool:
        """`if (x == y)` right after `x := y` on the same path."""
        m = self._EQ_RE.match(cond_str)
        return bool(m) and assigned.get(m.group(1).strip()) == m.group(2).strip()

    def find_next_states(self, path_list_str: List[UniqueNode], operation_tree: DiGraph, op_node: Any, nest_depth: int,
                         assigned: dict = None):
        next_operations = list(operation_tree.successors(op_node))
        assigned = dict(assigned or {})
        m = self._ASSIGN_RE.match(operation_tree.nodes[op_node].get('op_str', '') or '')
        if m:
            lhs, rhs = m.group(1), m.group(2).strip()
            assigned = {k: v for k, v in assigned.items() if k != lhs and v != lhs}
            assigned[lhs] = rhs

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
            self.find_next_states(path_list_str, operation_tree, next_operation, new_nest_depth, assigned)

            # Add end if closure
            if op_is_cond:
                path_list_str.append(UniqueNode(self.add_tabs(self.pcc_to_slicc.gen_condition_end(), nest_depth)))

        # Branches pruned by the generator (combinations of the variables the composed controller
        # is not supposed to reach, e.g. a manager in S with no L1 sharer left): fail loudly instead
        # of leaving the message in the queue without a transition
        conditions = [op for op in next_operations
                      if str(op) in (ProtoParserBase.k_cond, ProtoParserBase.k_ncond)]
        if conditions and len(conditions) == len(next_operations) and not self._exhaustive(conditions) \
                and not any(self._decided(operation_tree.nodes[op]['op_str'], assigned) for op in conditions):
            label = getattr(self, "handler_label", "").replace('"', "'")
            path_list_str.append(UniqueNode(self.add_tabs(
                f"else {{{self.nl}{self.tab}error(\"{label}: no branch for the current variables\");"
                f"{self.nl}}}", nest_depth)))
