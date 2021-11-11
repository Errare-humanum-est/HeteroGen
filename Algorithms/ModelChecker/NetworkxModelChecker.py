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

import itertools
from typing import List, Dict, Set, Tuple, Union, FrozenSet, Any
import networkx as nx
from graphviz import Digraph

from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.ClassSystemTuple import SystemTuple
from DataObjects.ClassMachine import Machine
from DataObjects.ClassMultiDict import MultiDict
from DataObjects.FlowDataTypes.ClassBaseAccess import Access, Evict
from DataObjects.ClassTrace import Trace
from Algorithms.ModelChecker.TraceChecker.TraceCheckGraph import TraceCheckGraph

from Debug.Monitor.ClassDebug import Debug
from Debug.Graphv.ParserNetworkxGraph import ParserPCCGraph
from collections import Counter, OrderedDict


## Object used to represent system states, it enables the NetworkxModelChecker to apply symmetry reduction
#  This class is essentially a set considers the count of multiple items of same type
#
class SystemStateTupleIdentifier:
    def __init__(self, state_tuple: Tuple[State_v2], system_tuple: SystemTuple):
        self.state_tuple = state_tuple
        self.state_counter_set_dict = {}

        self.mach_arch_tuple = tuple(mach.arch for mach in system_tuple.system_tuple)

        for state in state_tuple:
            if state in self.state_counter_set_dict:
                self.state_counter_set_dict[state] += 1
            else:
                self.state_counter_set_dict[state] = 0

    def __str__(self):
        return "; ".join(str(state) for state in self.state_tuple)

    def __hash__(self):
        return hash(frozenset([tuple([k, v]) for k, v in self.state_counter_set_dict.items()]))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def get_arch_state_pairs(self) -> Tuple[Tuple[FlatArchitecture, State_v2], ...]:
        return tuple(zip(self.mach_arch_tuple, self.state_tuple))


## Generate the initial system tuple dynamically
#  Function generates the initial system tuple dynamically
#
class SystemTupleGenerator:
    def __init__(self, arch_set: Set[FlatArchitecture], mach_count=0):
        self.arch_set: Set[FlatArchitecture] = arch_set
        self.access_arch_set: Tuple[FlatArchitecture] = self.get_access_arch_set(arch_set)
        self.comb_count = len(self.access_arch_set)
        if mach_count > self.comb_count:
            self.comb_count = mach_count

    @staticmethod
    def get_access_arch_set(arch_set: Set[FlatArchitecture]) -> Tuple[FlatArchitecture]:
        access_arch_set = set()
        for arch in arch_set:
            if [trans.guard for trans in arch.get_architecture_transitions() if isinstance(trans.guard, Access)]:
                access_arch_set.add(arch)
        Debug.perror("No accesses found in architecture", access_arch_set)
        return tuple(sorted(access_arch_set, key=lambda arch: str(arch)))

    def iter_init_system_tuples(self):
        for access_arch_tuple in itertools.product(self.access_arch_set, repeat=self.comb_count):
            yield self.gen_init_mcsd_system_tuple(access_arch_tuple)

    # Generate a simple multiple cache, single directory system tuple
    def gen_init_mcsd_system_tuple(self, access_arch_tuple: Tuple[FlatArchitecture]):
        func_arch_tuple = tuple(sorted(self.arch_set.difference(access_arch_tuple), key= lambda arch: str(arch)))
        return SystemTuple(tuple(Machine(arch) for arch in access_arch_tuple + func_arch_tuple))


class SystemStateSpaceChecker:
    def __init__(self, init_tuple: SystemTuple):
        self.full_check = True

        self.init_state_space_tuple = SystemStateTupleIdentifier(init_tuple.get_final_state_tuple(), init_tuple)

        # Dict [start_state_set, List[SystemTuples]]
        self.state_space_dict: MultiDict = MultiDict()
        self.state_space_dict[self.init_state_space_tuple] = init_tuple
        self.explore_state_space()

    def explore_state_space(self):
        cur_system_state_list = [self.init_state_space_tuple]
        next_system_state_list = []
        while True:
            for cur_system_state in cur_system_state_list:
                next_system_state_list += self.find_next_system_states(self.state_space_dict[cur_system_state][0])

            # No new system state
            if not next_system_state_list:
                break

            cur_system_state_list = next_system_state_list
            next_system_state_list = []

    def check_ordering_string(self, new_sytem_tuples):
        pass

    def find_next_system_states(self, system_tuple: SystemTuple):
        new_system_tuple_list = self.gen_new_system_tuples(system_tuple)
        if self.full_check:
            new_system_tuple_list = self.trace_check_graph(new_system_tuple_list)

        new_final_state_tuples = []
        # The remaining system tuples are valid, add them to the state space dict
        for new_system_tuple in new_system_tuple_list:
            final_system_state_tuple = SystemStateTupleIdentifier(new_system_tuple.get_final_state_tuple(),
                                                                  new_system_tuple)
            if final_system_state_tuple not in self.state_space_dict:
                new_final_state_tuples.append(final_system_state_tuple)
                self.state_space_dict[final_system_state_tuple] = new_system_tuple
            elif new_system_tuple not in self.state_space_dict[final_system_state_tuple]:
                self.state_space_dict[final_system_state_tuple] = new_system_tuple

        return new_final_state_tuples

    ## Returns a list of new system tuples that are checked for correctness
    #  @param self, trace_tuple: system_tuple: SystemTuple), return->List[SystemTuple]
    def gen_new_system_tuples(self, system_tuple: SystemTuple) -> List[SystemTuple]:
        mach_list_trace_list: List[List[Union[Trace, None]]] = []
        for mach in system_tuple.system_tuple:
            mach_list_trace_list.append(self.get_next_state_traces(mach))

        next_state_trace_tuple_dict: OrderedDict[FrozenSet, Tuple[Any]] = OrderedDict()

        # Iterate over the possible to generate products
        for mach_trace_tuple in itertools.product(*mach_list_trace_list):
            # There must exist exactly one access guard per atomic execution
            if not self.check_single_atomic_access(mach_trace_tuple):
                continue
            # Check that the set of incoming and outgoing messages are identical
            if not self.check_message_set_match(mach_trace_tuple):
                continue

            # If tuples have identical traces it is likely that multicasting in involved, add the tuple with most
            # concurrent traces to the dict
            if frozenset(mach_trace_tuple) in next_state_trace_tuple_dict:
                next_state_trace_tuple_dict[frozenset(mach_trace_tuple)] = self.check_replicated_traces(
                    next_state_trace_tuple_dict[frozenset(mach_trace_tuple)], mach_trace_tuple)
            else:
                next_state_trace_tuple_dict[frozenset(mach_trace_tuple)] = mach_trace_tuple

        new_system_tuples: List[SystemTuple] = []
        for next_state_trace_tuple in next_state_trace_tuple_dict:
            mach_trace_zip = list(zip(system_tuple.system_tuple, next_state_trace_tuple_dict[next_state_trace_tuple]))
            new_system_tuples.append(SystemTuple(tuple([entry[0].update_trace(entry[1]) for entry in mach_trace_zip])))

        new_system_tuples.sort(key=lambda x: str(x))

        return new_system_tuples

    ## Runs the trace checker that performs a rudimentary sequential execution check of the tuple traces
    #  @param system_tuple_list: List[SystemTuple], List[SystemTuple]
    @staticmethod
    def trace_check_graph(system_tuple_list: List[SystemTuple]) -> List[SystemTuple]:
        checked_tuples = []
        for system_tuple in system_tuple_list:
            trace_check_graph = TraceCheckGraph(system_tuple)
            # Check if a trace exists that covers all transitions
            if trace_check_graph.get_trans_traces():
                checked_tuples.append(system_tuple)
        return checked_tuples

    ## Return true if in tuple of traces only a single trace has an evict or access operation
    #  @param self, trace_tuple: Tuple[Trace]), return->bool
    @staticmethod
    def check_single_atomic_access(trace_tuple: Tuple[Any]) -> bool:
        access_list = [trace.init_guard for trace in trace_tuple
                       if isinstance(trace, Trace) and isinstance(trace.init_guard, (Access, Evict))]
        if len(access_list) == 1:
            return True
        return False

    ## Return true if in tuple of traces the set of input and output messages match
    #  @param self, trace_tuple: Tuple[Trace]), return->bool
    @staticmethod
    def check_message_set_match(trace_tuple: Tuple[Any]) -> bool:
        in_msg_set = set()
        out_msg_set = set()
        for trace in trace_tuple:
            if not trace:
                continue
            if trace.guards_msg:
                in_msg_set.update(set(str(msg) for msg in trace.guards_msg))
            if trace.out_msg:
                out_msg_set.update(set(str(msg) for msg in trace.out_msg))

        if in_msg_set == out_msg_set:
            return True
        return False

    ## Return the trace tuple with the smaller number of None traces
    @staticmethod
    def check_replicated_traces(cur_tuple: Tuple[Any], new_tuple: Tuple[Any]) -> Tuple[Any]:
        return cur_tuple if cur_tuple.count(None) >= new_tuple.count(None) else new_tuple

    ## Return all possible next traces for current final state of machine
    #  @param self, mach: Machine, return->List[Union[None, Trace]]
    @staticmethod
    def get_next_state_traces(mach: Machine) -> List[Union[None, Trace]]:
        state_traces = []
        start_state = mach.final_state
        stable_states = mach.arch.stable_states
        for trans_tree in mach.arch.state_sub_tree_dict[start_state]:
            state_traces += mach.arch.get_trans_traces(trans_tree, start_state, stable_states)

        return [Trace(state_trace) for state_trace in state_traces] + [None]


class NetworkxModelChecker:
    def __init__(self,
                 arch_set: Set[FlatArchitecture],
                 dbg_enable: bool = False):

        if None in arch_set:
            arch_set.remove(None)

        self.mach_term_cond = 2

        # Run the model checker and get system tuples
        networkx_checker_result: SystemStateSpaceChecker = self.run_checker(arch_set)

        self.valid_system_states: List[SystemStateTupleIdentifier] = []
        self.state_tuple_list: List[SystemTuple] = []


        self.get_state_tuples(networkx_checker_result)

        #self.custom_prune()

        # Sort the state tuple list
        self.state_tuple_list.sort(key=lambda x: str(x.get_access_trace()))

        # Update the architecture state access permission listing
        for arch in arch_set:
            arch.gen_system_state_access_map(self.state_tuple_list)

        if dbg_enable:
            self.draw_allowed_system_tuples()

    # This doesn't work for non inclusive protocols like RCC
    def custom_prune(self):
        revised_state_tuple_list = []
        for system_tuple in self.state_tuple_list:
            dir = system_tuple.system_tuple[-1]
            if dir.final_state == dir.arch.init_state:
                remote_states = set([cache.final_state for cache in system_tuple.system_tuple[0:-1]])
                if len(remote_states) > 1 or list(remote_states)[0] != system_tuple.system_tuple[0].arch.init_state:
                    continue
            revised_state_tuple_list.append(system_tuple)

    def run_checker(self, arch_set: Set[FlatArchitecture]) -> SystemStateSpaceChecker:
        covered_traces = 0
        mach_count = 0
        prev_trace_coverage_dict: Dict[int, SystemStateSpaceChecker] = {}
        while True:
            trace_coverage_dict: Dict[int, SystemStateSpaceChecker] = {}
            sys_tuple_generator = SystemTupleGenerator(arch_set, mach_count)
            mach_count = sys_tuple_generator.comb_count
            # Iterate over the new possible initial system tuples
            for init_tuple in sys_tuple_generator.iter_init_system_tuples():
                networkx_checker = SystemStateSpaceChecker(init_tuple)
                trace_count = self.trace_coverage_checker(init_tuple)
                trace_coverage_dict[trace_count] = networkx_checker

            max_coverage = max(trace_coverage_dict.keys())
            if max_coverage == covered_traces:
                # Return the slightly smaller system tuple that full filled the required conditions
                return prev_trace_coverage_dict[max_coverage]

            covered_traces = max_coverage

            # Increase the machine count for the next iteration
            prev_trace_coverage_dict = trace_coverage_dict

            if 0 < self.mach_term_cond == mach_count:
                return trace_coverage_dict[max_coverage]

            mach_count += 1


    @staticmethod
    def trace_coverage_checker(init_tuple: SystemTuple) -> int:
        init_tuple_arch_dict = {arch: 0 for arch in init_tuple.get_machine_architectures()}
        for mach in init_tuple.system_tuple:
            if len(mach.covered_traces) > init_tuple_arch_dict[mach.arch]:
                init_tuple_arch_dict[mach.arch] = len(mach.covered_traces)
        return sum(init_tuple_arch_dict.values())

    ## Find allowed state space tuples by building the evict tree
    # Assumption there must exist an evict tree path, only system states that have a path of evict edges ending in the
    # initial state are considered to be valid
    @staticmethod
    def build_evict_tree(networkx_checker_result: SystemStateSpaceChecker):
        evict_tree = nx.MultiDiGraph()
        state_tuple_node_dict = {networkx_checker_result.init_state_space_tuple:
                                     networkx_checker_result.init_state_space_tuple}
        for final_state_space_tuple in networkx_checker_result.state_space_dict:
            if final_state_space_tuple not in state_tuple_node_dict:
                state_tuple_node_dict[final_state_space_tuple] = final_state_space_tuple
            else:
                final_state_space_tuple = state_tuple_node_dict[final_state_space_tuple]

            for system_tuple in networkx_checker_result.state_space_dict[final_state_space_tuple]:
                access_trace = system_tuple.get_access_trace()
                if access_trace and isinstance(access_trace.init_guard, Evict):
                    start_state_space_tuple = SystemStateTupleIdentifier(system_tuple.get_start_state_tuple(),
                                                                         system_tuple)
                    if start_state_space_tuple not in state_tuple_node_dict:
                        state_tuple_node_dict[start_state_space_tuple] = start_state_space_tuple
                    else:
                        start_state_space_tuple = state_tuple_node_dict[start_state_space_tuple]

                    evict_tree.add_edge(start_state_space_tuple, final_state_space_tuple)

        #ParserPCCGraph.debug_process_graph(evict_tree, "Dummy", True)

        return list(nx.bfs_tree(evict_tree, networkx_checker_result.init_state_space_tuple, reverse=True).nodes)

    def get_state_tuples(self, networkx_checker_result: SystemStateSpaceChecker):
        self.valid_system_states: List[SystemStateTupleIdentifier] = self.build_evict_tree(networkx_checker_result)
        for system_state_space in networkx_checker_result.state_space_dict:
            for system_tuple in networkx_checker_result.state_space_dict[system_state_space]:
                #if SystemStateTupleIdentifier(system_tuple.get_start_state_tuple(), system_tuple) in self.valid_system_states:
                if self.check_system_tuple_is_valid_system_state(system_tuple):
                    if system_tuple.get_traces():
                        self.state_tuple_list.append(system_tuple)
                    else:
                        # The initial state tuple exists exactly once so check the trace coverage for it
                        self.check_trace_coverage(system_tuple)

    # A system tuple is only valid if
    def check_system_tuple_is_valid_system_state(self, system_tuple: SystemTuple) -> bool:
        start_state_exists = False
        final_state_exists = False

        for system_state in self.valid_system_states:
            if not start_state_exists and Counter(system_tuple.get_arch_start_state_pairs()) == \
                    Counter(system_state.get_arch_state_pairs()):
                start_state_exists = True
            if not final_state_exists and Counter(system_tuple.get_arch_final_state_pairs()) == \
                    Counter(system_state.get_arch_state_pairs()):
                final_state_exists = True
            if start_state_exists and final_state_exists:
                return True
        return False


    def update_state_tuple_mach_archs(self, old_arch, new_arch):
        for state_tuple in self.state_tuple_list:
            state_tuple.update_machine_archs(old_arch, new_arch)

    @staticmethod
    def check_trace_coverage(system_tuple: SystemTuple):
        for arch in system_tuple.get_machine_architectures():
            machines = system_tuple.get_arch_machines(arch)
            covered_traces_dict: Dict[int, Trace] = {}
            for mach in machines:
                for trace in mach.covered_traces:
                    covered_traces_dict[hash(trace)] = trace

            for state in arch.stable_states:
                for sub_tree in arch.state_sub_tree_dict[state]:
                    for trace in arch.get_trans_traces(sub_tree, state, arch.stable_states):
                        trace = Trace(trace)
                        if hash(trace) not in covered_traces_dict:
                            Debug.pwarning("Trace: " + str(trace) + " never taken by SSP state space exploration")


    def draw_allowed_system_tuples(self):
        self.draw_mod_check_system_tuples(self.state_tuple_list)

    @staticmethod
    def draw_mod_check_system_tuples(system_tuple_list: List[SystemTuple]):
        if not system_tuple_list:
            return

        name = "SystemTupleOutput"
        graph = Digraph(comment=name, engine='dot')

        state_tuples = {}
        for state_tuple in system_tuple_list:
            tuple_id = (state_tuple.start_state_tuple_str(),
                        state_tuple.final_state_tuple_str(),
                        state_tuple.access_state_tuple_str())
            state_tuples[tuple_id] = state_tuple

        for state_tuple in state_tuples.values():
            graph.edge(state_tuple.start_state_tuple_str(),
                       state_tuple.final_state_tuple_str(),
                       label=state_tuple.access_state_tuple_str())

        graph.render('level_state_tuples/' + name + '.gv', view=True)
