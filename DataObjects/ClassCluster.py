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

from typing import Tuple, List, Set
from DataObjects.ClassMachine import Machine
from DataObjects.ClassLevel import Level
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.Architecture.ClassGlobalBaseArchitecture import GlobalBaseArchitecture

from DataObjects.ClassSystemTuple import SystemTuple


class Cluster(SystemTuple):

    def __init__(self, machines: Tuple[Machine, ...], cluster_id: str, update_mach_ids: bool = True):
        SystemTuple.__init__(self, machines)
        self.cluster_id = ""
        self.update_global_architectures_cluster_id(cluster_id, update_mach_ids)

    def __str__(self):
        return str(self.cluster_id)

    def update_global_architectures_cluster_id(self, cluster_id: str, update_mach_ids=False):
        self.cluster_id = cluster_id
        if update_mach_ids:
            for global_arch in self.get_global_architectures():
                global_arch.update_global_identifiers(cluster_id)

    def get_global_architectures(self) -> Set[GlobalBaseArchitecture]:
        global_arch_set: Set[GlobalBaseArchitecture] = set()
        for machine in self.system_tuple:
            global_arch_set.add(machine.arch.global_arch)
        return global_arch_set

    def get_machine_architectures(self) -> Set[FlatArchitecture]:
        mach_arch_set: Set[FlatArchitecture] = set()
        for machine in self.system_tuple:
            mach_arch_set.add(machine.arch)
        return mach_arch_set

    def get_machine_architecture_count(self, mach_arch: FlatArchitecture) -> int:
        mach_arch_list = []
        for machine in self.system_tuple:
            if machine.arch == mach_arch:
                mach_arch_list.append(machine.arch)
        return len(mach_arch_list)


    ''' #HIERAGEN
    def replace_arch(self, old_arch: FlatArchitecture, new_arch: FlatArchitecture):
        # Then replace the directory
        found_once = 0
        for machine in self.system_tuple:
            machine.arch.update_trans_operation(old_arch.get_unique_id_str(), new_arch.get_unique_id_str())
            if machine.arch == old_arch and not found_once:
                machine.update_mach_arch(new_arch)
                found_once = 1
        assert found_once, "Could not find architecture to replace in cluster"
    '''





