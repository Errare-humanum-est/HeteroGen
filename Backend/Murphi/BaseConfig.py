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

from typing import List, Tuple, Dict, Union
from collections import OrderedDict

from DataObjects.ClassCluster import Cluster
from DataObjects.ClassMachine import Machine

from Debug.Monitor.ClassDebug import Debug

from MurphiLitmusTests.ClassLitmusTest import LitmusTest


class BaseConfig(Debug):

    # Litmus testing enabled
    litmus_test_dir = ""

    # Ordered network type specification
    # Bus False (Total order)
    # Network True (Point to point ordering)
    ordered_network_dict = {"Bus": True, "Network": False}

    ## Config Parameters
    # Disable evicts (Evicts can cause progress even if protocol is flawed), evicts must not be used to ensure progress
    enable_evicts: bool = True                    # Default true

    # Enable import FIFOs at controllers
    enable_fifo: bool = False

    # Enable atomic events
    atomic_events: bool = True

    # Enable simple ordered network (These networks are total ordered, but much faster in simulation)
    ordered_network_type: str = "Bus"
    enable_total_order_network: bool = ordered_network_dict[ordered_network_type]

    # Enable read/write execution
    enable_read_write_execution: bool = False

    # Invariants, if true properties are checked
    check_write_linearization: bool = False
    check_exclusive_write: bool = False

    c_fifo_max: int = 0         # Buffer size cnt+1

    def __init__(self,  clusters: List[Cluster], litmus_test: Union[LitmusTest, None] = None):
        Debug.__init__(self)

        # Super message definition
        self.super_type_defs = OrderedDict()
        # Vector definitions common across all architectures in Murphi
        self.var_vector_map: Dict[str, str] = {}

        self.litmus_test = litmus_test

        # If litmus testing is not activated
        self.c_adr_max: int = 1  # Scalarset
        self.c_val_max: int = 1  # Range 0..N
        self.litmus_testing = False
        self.c_cpu_count = 0
        self.c_instr_count = 0

        if litmus_test:
            # Litmus testing
            self.c_cpu_count = len(litmus_test.threads)
            self.c_instr_count = litmus_test.instruction_count - 1          # Range 0..N
            self.c_adr_max: int = len(litmus_test.variable_adr_dict) - 1    # Range 0..N
            self.c_val_max: int = litmus_test.value_max                     # Range 0..N

            self.litmus_testing = True

        # Total global machine count (relevant for network size calculation)
        self.total_mach_cnt = self.get_machine_count(clusters)

        self.c_ordered_cnt = (self.total_mach_cnt + 1) * (self.c_adr_max + 1)
        self.c_unordered_cnt = self.c_ordered_cnt

    def exist_vector_type(self, vector_def: str, vector_type: str) -> bool:
        if vector_def in self.var_vector_map and self.var_vector_map[vector_def] != vector_type:
            self.perror("Mismatching vector definitions for vector type: " + vector_def + ":")
            self.perror("First declaration: " + vector_type)
            self.perror("Second declaration: " + self.var_vector_map[vector_def])

        if vector_def in self.var_vector_map:
            return True
        else:
            self.var_vector_map[vector_def] = vector_type
            return False

    ## Determine number of machines in simulation environment
    #
    def get_machine_count(self, clusters: List[Cluster]):
        total_mach_cnt = 0
        for cluster in clusters:
            machines: Tuple[Machine] = cluster.system_tuple
            for arch in cluster.get_machine_architectures():
                # Get the number of machines defined in the input SSP
                arch_cnt = 1
                if arch.machine.machine_cnt_const_id:
                    arch_cnt = int(arch.global_arch.constants.const_dict[arch.machine.machine_cnt_const_id])

                # Count the number of machines of type in cluster
                mach_cnt = len([mach for mach in machines if arch in mach.get_arch_list()])

                if arch_cnt != mach_cnt:
                    arch.global_arch.constants.const_dict[arch.machine.machine_cnt_const_id] = str(mach_cnt)
                    self.pwarning("Cluster machine count: " + str(mach_cnt) +
                                  " SSP machine definition count: " + str(arch_cnt) +
                                  " mismatch, using cluster count")
                    total_mach_cnt += mach_cnt
                else:
                    total_mach_cnt += arch_cnt

        return total_mach_cnt
