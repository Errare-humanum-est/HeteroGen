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

#
#
#

from typing import Tuple, List, FrozenSet
from DataObjects.ClassMachine import Machine
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.ClassTrace import Trace
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess, Access, Evict
from DataObjects.FlowDataTypes.ClassEvent import Event

from itertools import product, permutations


class SystemTuple:
    def __init__(self, machines: Tuple[Machine, ...]):
        self.system_tuple: Tuple[Machine] = machines

    def __str__(self):
        return "; ".join([mach.get_mach_state_trace_str() for mach in self.system_tuple])

    def __hash__(self):
        return hash(tuple(hash(mach) for mach in self.system_tuple))

    def make_simple_set(self):
        return tuple(sorted([hash(mach) for mach in self.system_tuple])).__hash__()

    def __eq__(self, other):
        if isinstance(other, SystemTuple):
            return hash(self) == hash(other)
        return False

    def __len__(self):
        return len(self.system_tuple)

    # TODO: LEGACY V1,V2
    def get_start_state_set(self) -> FrozenSet:
        return frozenset([mach.start_state for mach in self.system_tuple])

    # TODO: LEGACY V1,V2
    def get_final_state_set(self) -> FrozenSet:
        return frozenset([mach.final_state for mach in self.system_tuple])

    def get_start_state_tuple(self) -> Tuple:
        return tuple([mach.start_state for mach in self.system_tuple])

    def get_final_state_tuple(self) -> Tuple:
        return tuple([mach.final_state for mach in self.system_tuple])

    def get_traces(self) -> List[Trace]:
        mach_traces = []
        for mach in self.system_tuple:
            if mach.cur_trace:
                mach_traces.append(mach.cur_trace)
        return mach_traces

    # TODO: LEGACY V1,V2
    def get_reduced_set(self):
        unique_state_dict = {id(mach.cur_trace): mach for mach in self.system_tuple if mach.cur_trace}
        sorted_tuple = sorted(list(unique_state_dict.values()), key=lambda mach: mach.get_mach_state_trace_id())
        return hash(tuple(sorted(unique_state_dict.keys()))), sorted_tuple

    def get_permutation_machines(self) -> List[Tuple[Machine]]:
        # Only identical blocks may be permutated
        arch_list = self.get_machine_architectures()
        mach_list = {arch: [] for arch in arch_list}
        for mach in self.system_tuple:
            (mach_list[mach.arch]).append(mach)

        for entry in mach_list:
            perm = list(permutations(mach_list[entry], len(mach_list[entry])))
            mach_list[entry] = perm

        new_system_tuples = []
        for raw_system_tuple in list(product(*mach_list.values())):
            new_sys_tuple = ()
            for arch_tuple in raw_system_tuple:
                new_sys_tuple += arch_tuple

            new_system_tuples.append(new_sys_tuple)

        return new_system_tuples

    def get_machine_architectures(self) -> List[FlatArchitecture]:
        arch_list = []
        for mach in self.system_tuple:
            if mach.arch not in arch_list:
                arch_list.append(mach.arch)
        return arch_list

    def get_arch_machines(self, arch) -> List[Machine]:
        arch_machines = []
        for mach in self.system_tuple:
            if mach.arch == arch:
                arch_machines.append(mach)
        return arch_machines

    def get_arch_traces(self, arch: FlatArchitecture) -> List[Trace]:
        return [mach.cur_trace for mach in self.get_arch_machines(arch) if mach.cur_trace]

    def get_access_trace(self) -> Trace:
        for mach in self.system_tuple:
            if mach.cur_trace and isinstance(mach.cur_trace.init_guard, (Access, Evict)):
                return mach.cur_trace

    def get_arch_access_trace(self, arch: FlatArchitecture = None) -> List[Trace]:
        if arch:
            mach_traces = [mach.cur_trace for mach in self.get_arch_machines(arch)]
        else:
            mach_traces = [mach.cur_trace for mach in self.system_tuple]
        return [mach_trace for mach_trace in mach_traces if mach_trace
                and isinstance(mach_trace.init_guard, (BaseAccess.Access_type, Event))]

    def get_arch_remote_trace(self, arch: FlatArchitecture = None) -> List[Trace]:
        if arch:
            mach_traces = [mach.cur_trace for mach in self.get_arch_machines(arch)]
        else:
            mach_traces = [mach.cur_trace for mach in self.system_tuple]
        return [mach_trace for mach_trace in mach_traces if mach_trace
                and not isinstance(mach_trace.init_guard, BaseAccess.Access_type)]

    def sort_machines_id(self) -> Tuple[Machine]:
        # Get list of architectures first:
        mach_list = list(self.system_tuple)
        mach_arch_sort = tuple(sorted(mach_list, key=lambda machine: (str(machine.arch), id(machine.covered_traces))))
        return mach_arch_sort

    def find_traces(self, trace: Trace) -> bool:
        for mach in self.system_tuple:
            if trace == mach.cur_trace:
                return True
        return False

    def sort_and_update_system_tuple(self) -> 'SystemTuple':
        self.system_tuple = self.sort_machines_id()
        return self

    def sort_machines_state(self, state_type: str = "start_state") -> Tuple[Machine]:
        # Get list of architectures first:
        mach_list = list(self.system_tuple)
        mach_arch_sort = tuple(sorted(mach_list, key=lambda machine: (machine.arch.arch_name,
                                                                      str(getattr(machine, state_type)))))
        return mach_arch_sort

    def start_state_tuple_str(self):
        sorted_tuple = self.sort_machines_state("start_state")
        start_state_str = ""
        for mach in sorted_tuple:
            start_state_str += str(mach.start_state) + "; "

        return start_state_str[:-2]

    def final_state_tuple_str(self):
        sorted_tuple = self.sort_machines_state("final_state")
        final_state_str = ""
        for mach in sorted_tuple:
            final_state_str += str(mach.final_state) + "; "

        return final_state_str[:-2]

    def access_state_tuple_str(self):
        sorted_tuple = self.sort_machines_state("start_state")
        access_str = ""
        guard_list = ""
        for mach in sorted_tuple:
            if not mach.cur_trace:
                continue
            new_access_str = str(mach.cur_trace.init_guard)
            if isinstance(mach.cur_trace.init_guard, BaseAccess.Access_type) or \
                    mach.cur_trace.init_guard in mach.arch.event_network.event_issue.values():
                access_str = new_access_str
            elif new_access_str:
                guard_list += new_access_str + "; "

        if guard_list:
            return access_str + "; " + guard_list[:-2]
        else:
            return access_str

    def system_tuple_id_str(self):
        sorted_tuple = self.sort_machines_id()
        sys_id = ""
        for mach in sorted_tuple:
            sys_id += mach.arch.arch_name + "_" + mach.arch.arch_name + "; "

        return sys_id[:-2]
