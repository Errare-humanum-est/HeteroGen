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
from DataObjects.ClassCluster import Cluster
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess

from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates
from Backend.Murphi.BaseConfig import BaseConfig

from Debug.Monitor.ClassDebug import Debug


class GenCPULitmusServeCPU(TemplateHandler, Debug):

    instr_access_str = "instr.access"

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        TemplateHandler.__init__(self)
        Debug.__init__(self)
        if config.litmus_testing:
            murphi_str.append("------" + __name__.replace('.','/') + self.nl + self.add_tabs(self.gen_cpu_access_func(clusters), 1))

    def gen_cpu_access_func(self, clusters: List[Cluster]) -> str:
        access_func_str = ''

        exec_archs = set()
        for cluster in clusters:
            archs = cluster.get_machine_architectures()
            for arch in archs:
                for state in arch.stable_states:
                    if [trans for trans in state.state_trans if isinstance(trans.guard, BaseAccess.Access)]:
                        exec_archs.add(arch)
                        access_func_str += self.cpu_try_access(arch)
                        break

        self.perror("Unable to identify caches that can serve accesses", exec_archs)
        exec_body_str = self.gen_serve_body(exec_archs)
        access_func_str += self.gen_cpu_serve_func(exec_body_str)

        return access_func_str

    def cpu_try_access(self, arch: FlatArchitecture):
        access_load_str = self.gen_access_str(arch, BaseAccess.k_load)
        access_store_str = self.gen_access_str(arch, BaseAccess.k_store)

        no_access_str = self.gen_access_str(arch, str(None))

        if no_access_str:
            no_access_str = self._stringReplKeys(self._openTemplate(MurphiTemplates.f_cpu_dummy_access),
                                                 [no_access_str]) + self.nl

        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_cpu_try_access),
                                    [str(arch),
                                     MurphiTokens.v_cache_block,
                                     access_load_str,
                                     access_store_str,
                                     no_access_str]
                                    ) + self.nl

    def gen_serve_body(self, arch_set: Set[FlatArchitecture]):
        exec_str = ''

        for arch in arch_set:
            exec_str += self._stringReplKeys(self._openTemplate(MurphiTemplates.f_cpu_serve_body),
                                             [MurphiTokens.k_obj_set, str(arch)]) + self.nl
        return exec_str

    def gen_cpu_serve_func(self, exec_str: str):
        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_cpu_serve_head),
                                    [MurphiTokens.k_machines, exec_str]) + self.nl

    def gen_access_str(self, arch: FlatArchitecture, ref_access: str):
        access_ret_str = ""

        for access in arch.global_arch.base_access.access_to_base_access_map:
            for access_entry in arch.global_arch.base_access.access_to_base_access_map[access]:
                if str(access_entry) == str(ref_access):
                    access_ret_str += self.instr_access_str + " = " + str(access) + "|"

        if access_ret_str:
            access_ret_str = "(" + access_ret_str[:-1] + ") & "

        return access_ret_str

