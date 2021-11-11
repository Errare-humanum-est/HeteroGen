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
from typing import Dict, List, Set

from DataObjects.Architecture.ArchitectureClassification import ArchitectureClassification
from Algorithms.ProtoAlgoNetworkx.StateSetsNetworkx import StateSetsNetworkx
from DataObjects.CommClassification.ClassCommClassFunc import CommClassFunc
from DataObjects.Architecture.ClassBaseArchitecture import BaseArchitecture
from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.FlowDataTypes.ClassBaseAccess import Access
from DataObjects.ClassMultiDict import MultiDict
from DataObjects.ClassTrace import Trace

from collections import Counter
from itertools import chain

## FlatArchitecture
#
#  FlatArchitecture inherits from BaseArchitecture and registers the architecture with the GlobalBaseArchitecture,
#  which is responsible for renaming variables, messages and so on. FlatArchitecture can be handled by ProtoGen. Any
#  child inheriting FlatArchitecture can be made concurrent by ProtoGen
class FlatArchitecture(BaseArchitecture,
                       StateSetsNetworkx, ArchitectureClassification):
    def __init__(self,
                 base_arch: BaseArchitecture,
                 gdbg: bool = False):

        # Generates the graph tree
        BaseArchitecture.__init__(self, gdbg)
        BaseArchitecture.copy_base_architecture(self, base_arch)

        # The access permissions of the caches are mapped onto the current architecture states
        self.stable_state_access_permission_map: Dict[State_v2, Set[Access]] = \
            {state: set() for state in base_arch.stable_states}

        # Exclusive access permissions of cache states,
        # No other caches can perform this operation at the same time, but other operations are permitted
        self.stable_state_exclusive_access_permission_map: Dict[State_v2, Set[Access]] = \
            {state: set() for state in base_arch.stable_states}

        # Atomic access permission of cache states,
        # Stricter than exclusive, no other cache can perform memory operations at all
        self.stable_state_atomic_access_permission_map: Dict[State_v2, Set[Access]] = \
            {state: set() for state in base_arch.stable_states}

        # Generate the trace dictionary
        state_trans_trace_dict: MultiDict = MultiDict()
        for stable_state in self.stable_states:
            for trans_tree in self.state_sub_tree_dict[stable_state]:
                trans_trace_list = self.get_trans_traces(trans_tree, stable_state, self.stable_states)
                for trans_trace in trans_trace_list:
                    state_trans_trace_dict[stable_state] = Trace(trans_trace)

        # Use the system tuple results for the classification
        CommClassFunc(state_trans_trace_dict, self.global_arch)
        StateSetsNetworkx.__init__(self, state_trans_trace_dict)

        if gdbg:
            self.draw_controller()

    def __str__(self):
        return str(self.arch_name)

    def copy_flat_architecture(self, other):
        # State Classification
        self.stable_state_access_permission_map = other.stable_state_access_permission_map
        self.stable_state_exclusive_access_permission_map = other.stable_state_exclusive_access_permission_map
        self.stable_state_atomic_access_permission_map = other.stable_state_atomic_access_permission_map

    ####################################################################################################################
    # NetworkxModelChecker: Post model checking function
    ####################################################################################################################
    def gen_system_state_access_map(self, state_tuple_list: List['SystemTuple']):
        cache_state_access_map: Dict[State_v2, Set[Access]] = {}
        for system_tuple in state_tuple_list:
            cache_machines = [mach for mach in system_tuple.system_tuple if mach.arch.machine.check_cache()]
            dir_mem_machines = [mach for mach in system_tuple.system_tuple if mach not in cache_machines]
            # Check if machine is cache
            if self.machine.check_cache():
                cache_access_dict = self._get_cache_access_dict(cache_machines, [self])
                for state in cache_access_dict:
                    self.stable_state_access_permission_map[state].update(cache_access_dict[state])
            else:
                cache_archs = list(set(mach.arch for mach in cache_machines))
                cache_access_dict = self._get_cache_access_dict(cache_machines, cache_archs)
                for dir_machine in dir_mem_machines:
                    self.stable_state_access_permission_map[dir_machine.start_state].update(
                        set().union(*cache_access_dict.values()))

            self._state_add_access(cache_state_access_map, cache_access_dict)

        self._gen_system_state_exclusive_access_map(cache_state_access_map, state_tuple_list)

    @staticmethod
    def _get_cache_access_dict(cache_machines, arch_list: List[BaseArchitecture]) -> Dict[State_v2, Set[Access]]:
        cache_access_dict: Dict[State_v2, Set[Access]] = {}
        for machine in cache_machines:
            if machine.arch not in arch_list:
                continue
            if machine.cur_trace and isinstance(machine.cur_trace.init_guard, Access):
                # and not machine.cur_trace.out_msg):
                remote_traces = [remote_machine.cur_trace for remote_machine in cache_machines
                                 if remote_machine != machine and remote_machine.cur_trace]
                # If remote caches are affected by an access, then the access is not a hit
                if remote_traces:
                    continue
                # If an out message exists, the response must not affect the current cache state, because it would not
                # ba a hit.
                if machine.cur_trace.out_msg and machine.start_state != machine.final_state:
                    continue
                if machine.start_state in cache_access_dict:
                    cache_access_dict[machine.start_state].add(machine.cur_trace.init_guard)
                else:
                    cache_access_dict[machine.start_state] = {machine.cur_trace.init_guard}

        return cache_access_dict

    @staticmethod
    def _state_add_access(cache_state_access_map, cache_access_dict: Dict[State_v2, Set[Access]]):
        for state in cache_access_dict:
            if state not in cache_state_access_map:
                cache_state_access_map[state] = cache_access_dict[state]
            else:
                cache_state_access_map[state] = cache_state_access_map[state].union(cache_access_dict[state])

    ## Classify if accesses are globally atomic (no other cache has any access permissions at all) or exclusive
    # (other caches can still perform accesses of a different type)
    #  @param self; cache_state_access_map: Dict[State_v2, Set[Access]]; state_tuple_list: List['SystemTuple']
    #  @param cache_state_access_map: Dict[State_v2, Set[Access]] Dict that maps accesses to states in which
    #   they can happen in
    #  @param state_tuple_list: List['SystemTuple'] List of all system state tuples found by the model checker
    def _gen_system_state_exclusive_access_map(self,
                                               cache_state_access_map: Dict[State_v2, Set[Access]],
                                               state_tuple_list: List['SystemTuple']):
        for state in sorted(self.stable_state_access_permission_map, key=lambda x: str(x)):
            state_accesses: Set[Access] = set()
            caches_access_listing: List[List[List[Access]]] = []
            # Iterate over all system tuples
            for system_tuple in state_tuple_list:
                cache_machines = [mach for mach in system_tuple.system_tuple if mach.arch.machine.check_cache()]
                # If the current state exists in the system tuple as a start state
                if state in system_tuple.get_start_state_tuple():
                    access_list: List[List[Access]] = []
                    # Iterate over all machines
                    for cache_machine in cache_machines:
                        # If the machine start state is not in the cache_state_access_map yet, add the start_state to it
                        if cache_machine.start_state not in cache_state_access_map:
                            cache_state_access_map[cache_machine.start_state] = set()
                        # Add list of accesses to
                        access_list.append(list(cache_state_access_map[cache_machine.start_state]))
                        state_accesses |= cache_state_access_map[cache_machine.start_state]
                    caches_access_listing.append(access_list)

            for access in state_accesses:
                is_atomic: bool = True
                is_exclusive: bool = True
                for access_listing in caches_access_listing:
                    # Check if access is atomic, in no remote entry any access must be listed
                    occurence_count = [access_entry for access_entry in access_listing if access_entry]
                    if access in chain.from_iterable(occurence_count) and len(occurence_count) != 1:
                        is_atomic = False

                    # Check if the access is exclusive, in all access listings there must only exist a single access
                    # of this type
                    atomic_count = Counter(chain.from_iterable(access_listing))
                    if atomic_count[access] > 1:
                        is_exclusive = False

                # If an access is atomic, it is obviously also exclusive
                if is_atomic:
                    self.stable_state_atomic_access_permission_map[state].add(access)
                if is_exclusive:
                    self.stable_state_exclusive_access_permission_map[state].add(access)

    ####################################################################################################################
    # Hierarchical Functions
    ####################################################################################################################
    def get_flat_base_architecture(self):
        return self

    ####################################################################################################################
    # Backend Functions
    ####################################################################################################################
    def get_arch_list(self):
        return [self]
