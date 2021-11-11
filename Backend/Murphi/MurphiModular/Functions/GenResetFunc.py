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

from typing import List, Set

from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from DataObjects.ClassCluster import Cluster
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture

from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens

from Debug.Monitor.ClassDebug import Debug


class GenResetFunc(TemplateHandler, Debug):

    def __init__(self, murphi_str: List[str], clusters: List[Cluster]):
        TemplateHandler.__init__(self)
        Debug.__init__(self)

        ruleset_str_list = []

        arch_set: Set[FlatArchitecture] = set()

        for cluster in clusters:
            machines = set(cluster.system_tuple)

            for arch in set([machine.arch for machine in machines]):
                ruleset_str_list.append(self.gen_machine_reset(arch))
                arch_set.add(arch)

        ruleset_str_list.append(self.add_tabs(self.gen_global_machine_reset(arch_set), 1))

        murphi_str.append("----" + __name__.replace('.','/') + self.nl + self.add_tabs("".join(ruleset_str_list), 1))

    def gen_machine_reset(self, arch: FlatArchitecture) -> str:
        base_var_str = MurphiTokens.k_instance + str(arch) + "[i]." + MurphiTokens.v_cache_block + "[a]."
        init_var_str = base_var_str + self.gen_mach_state(arch)
        init_var_str += self.gen_data_init(arch, base_var_str)
        init_var_str += self.gen_variable_inits(arch, base_var_str)

        ret_str = self._stringReplKeys(self._openTemplate(MurphiTemplates.f_machine_reset_body),
                                       [
                                           MurphiTokens.k_reset_machines,
                                           str(arch),
                                           MurphiTokens.k_obj_set,
                                           MurphiTokens.k_address,
                                           self.add_tabs(init_var_str, 3)
                                       ]) + self.nl + self.nl
        return ret_str

    def gen_mach_state(self, arch: FlatArchitecture) -> str:
        return MurphiTokens.k_state + " := " + str(arch) + "_" + str(arch.init_state) + self.end

    def gen_data_init(self, arch: FlatArchitecture, base_var_str: str):
        data_init_str = ""
        for variable in arch.machine.variables:
            if str(arch.machine.variables[variable]) == ProtoParserBase.k_data:
                data_init_str += base_var_str + str(variable) + " := 0" + self.end
            elif variable not in arch.machine.variables_init_val:
                data_init_str += MurphiTokens.k_undefine + " " + base_var_str + str(variable) + self.end
        return data_init_str

    def gen_variable_inits(self, arch: FlatArchitecture, base_var_str: str) -> str:
        var_init_str = ""
        for variable in arch.machine.variables_init_val:
            var_init_val = str(list(arch.machine.variables_init_val[variable].getChildren())[-1])
            var_init_str += base_var_str + str(variable) + " := " + var_init_val + self.end
        return var_init_str

    def gen_global_machine_reset(self, arch_set: Set[FlatArchitecture]) -> str:
        arch_reset_str = ""

        for arch in arch_set:
            arch_reset_str += MurphiTokens.k_reset_machines + str(arch) + "()" + self.end

        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_reset_func),
                                    [MurphiTokens.k_reset_machines, arch_reset_str])

