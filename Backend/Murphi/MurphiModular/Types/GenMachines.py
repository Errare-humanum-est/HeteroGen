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

from typing import List, Dict

from DataObjects.ClassCluster import Cluster
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture

from Backend.Murphi.MurphiModular.General.GenAtomicEvent import AtomicEvent
from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Murphi.BaseConfig import BaseConfig
from Backend.Murphi.MurphiModular.Types.GenMachineEntry import GenMachineEntry
from Debug.Monitor.ClassDebug import Debug


class GenMachines(TemplateHandler, Debug):

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        TemplateHandler.__init__(self)
        Debug.__init__(self)

        self.arch_type_dict: Dict[FlatArchitecture, GenMachineEntry] = {}

        mach_type_str = ""

        for cluster in clusters:
            machines = set(cluster.system_tuple)
            archs = set([machine.arch for machine in machines])

            for arch in archs:
                arch_str = self.gen_machine_entry(arch, config)
                arch_str += self.gen_machine_event_queue(arch, config)
                arch_str += self.gen_machine_instance(arch)
                arch_str += self.gen_machine_objects(arch)

                mach_type_str += arch_str

        mach_type_str = "----" + __name__.replace('.','/') + self.nl + self.add_tabs(mach_type_str, 1) + self.nl

        murphi_str.append(mach_type_str)

    def gen_machine_entry(self, arch: FlatArchitecture, config: BaseConfig) -> str:
        type_def_str = ""
        arch_str = MurphiTokens.k_entry + str(arch) + ": record" + self.nl
        arch_str += self.tab + MurphiTokens.k_state + ": " + MurphiTokens.k_state_label + str(arch) + self.end

        # Record
        self.arch_type_dict[arch] = GenMachineEntry(arch)

        for variable in arch.machine.variables:
            # Create new variable assignment
            arch_str += self.tab + self.arch_type_dict[arch].gen_variable_def(variable,
                                                                              arch.machine.variables[variable])
        arch_str += "end" + self.end + self.nl

        for vector_def in self.arch_type_dict[arch].vector_defs:
            if not config.exist_vector_type(vector_def, self.arch_type_dict[arch].vector_defs[vector_def]):
                type_def_str += self.arch_type_dict[arch].vector_defs[vector_def]

        var_vector_map: Dict[str, str] = {}
        for var_def in self.arch_type_dict[arch].variable_type_map:
            if self.arch_type_dict[arch].variable_type_map[var_def] in self.arch_type_dict[arch].vector_defs:
                var_vector_map[var_def] = self.arch_type_dict[arch].variable_type_map[var_def]

        return type_def_str + self.nl + arch_str

    def gen_machine_event_queue(self, arch: FlatArchitecture, config: BaseConfig) -> str:
        if not arch.event_network.exist_events():
            return ""

        atomic_event_str = ""
        if config.atomic_events:
            atomic_event_str = AtomicEvent.atomic_event_lock_var + ": " + MurphiTokens.k_address + self.end

        # Generate the header
        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_event_queue_def),
                                    [MurphiTokens.k_event,
                                     str(arch),
                                     MurphiTokens.k_entry,
                                     MurphiTokens.k_address,
                                     MurphiTokens.k_event_label,
                                     MurphiTokens.c_adr_cnt_const,
                                     atomic_event_str
                                     ]) + self.nl + self.nl

    def gen_machine_instance(self, arch: FlatArchitecture) -> str:
        obj_str = ""
        obj_str += MurphiTokens.k_mach + str(arch) + ": record" + self.nl
        obj_str += (self.tab + MurphiTokens.v_cache_block + ": array[" + MurphiTokens.k_address + "] of " +
                    MurphiTokens.k_entry + str(arch) + self.end)
        if arch.event_network.exist_events():
            obj_str += self.tab + MurphiTokens.v_evt + ": " + MurphiTokens.k_event + str(arch) + self.end

        obj_str += "end" + self.end + self.nl

        return obj_str

    def gen_machine_objects(self, arch: FlatArchitecture) -> str:
        obj_str = ""
        obj_str += (MurphiTokens.k_object + str(arch) + ": array[" + MurphiTokens.k_obj_set + str(arch) + "] of " +
                    MurphiTokens.k_mach + str(arch) + self.end)
        return obj_str
