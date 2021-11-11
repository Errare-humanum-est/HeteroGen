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

from typing import List, Dict, Set
from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.ClassCluster import Cluster
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture

from Backend.Murphi.MurphiModular.General.GenAtomicEvent import AtomicEvent
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates
from Backend.Murphi.BaseConfig import BaseConfig

from Debug.Monitor.ClassDebug import Debug


class GenCPULitmusAccessCache(TemplateHandler, Debug):

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        TemplateHandler.__init__(self)
        Debug.__init__(self)
        self.config = config
        if config.litmus_testing:
            murphi_str.append("------" + __name__.replace('.', '/') + self.nl +
                              self.add_tabs(self.gen_cpu_access_func(clusters), 1))

    def gen_cpu_access_func(self, clusters: List[Cluster]) -> str:
        access_func_str = ''

        exec_archs = set()
        for cluster in clusters:
            archs = cluster.get_machine_architectures()
            for arch in archs:
                ret_str = self.cache_access_func(arch)
                if not ret_str:
                    continue
                exec_archs.add(arch)
                access_func_str += ret_str

        self.perror("Unable to identify caches that can serve accesses", exec_archs)
        exec_body_str = self.gen_execute_body(exec_archs)
        access_func_str += self.gen_cpu_issue_func(exec_body_str)

        return access_func_str

    def cache_access_func(self, arch: FlatArchitecture):
        states: List[State_v2] = arch.get_architecture_states()
        access_cache_str = ""

        access_trans_dict: Dict[State_v2, List[Transition_v2]] = {}

        found = False
        for state in states:
            access_trans_dict[state] = [trans for trans in state.state_trans
                                        if isinstance(trans.guard, BaseAccess.Access)]
            if access_trans_dict[state]:
                found = True

        if not found:
            return access_cache_str

        # Generate the header
        access_cache_str += self._stringReplKeys(self._openTemplate(MurphiTemplates.f_cpu_cache_access_head),
                                                 [str(arch), MurphiTokens.v_cache_block,
                                                  MurphiTokens.v_cbe, MurphiTokens.v_mach]) + self.nl

        access_cache_str += self.cache_access_evict(arch, access_trans_dict)

        access_cache_str += self._openTemplate(MurphiTemplates.f_cpu_cache_access_tail) + self.nl

        return access_cache_str + self.nl

    def cache_access_evict(self,
                           arch: FlatArchitecture,
                           access_trans_dict: Dict[State_v2, List[Transition_v2]]) -> str:
        rules_str = ""

        for state in access_trans_dict:
            trans_guard_list = []
            for transition in access_trans_dict[state]:
                    if str(transition.guard) in trans_guard_list:
                        continue
                    trans_guard_list.append(str(transition.guard))
                    rules_str += self.gen_cpu_state_cond(arch, transition)

        return rules_str

    def gen_cpu_state_cond(self, arch: FlatArchitecture, transition: Transition_v2):
        aux_checks_str = ""
        lock_func_str = ""

        if transition.out_msg:
            aux_checks_str += '& ' + MurphiTokens.f_network_ready + ' '

        if self.config.atomic_events:
            if AtomicEvent().check_atomic_event(arch, transition):
                aux_checks_str += '& ' + AtomicEvent().gen_test_atomic_event_func(arch)
                lock_func_str += AtomicEvent().gen_lock_atomic_event_func(arch) + self.nl

        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_cpu_cache_access_body),
                                    [
                                        MurphiTokens.v_cbe,
                                        MurphiTokens.k_state,
                                        str(arch) + "_" + str(transition.start_state),
                                        str(transition.guard),
                                        aux_checks_str,
                                        MurphiTokens.v_mach,
                                        lock_func_str + MurphiTokens.k_access_func,
                                    ]) + self.nl + self.nl

    def gen_execute_body(self, arch_set: Set[FlatArchitecture]):
        exec_str = ''

        for arch in arch_set:
            exec_str += self._stringReplKeys(self._openTemplate(MurphiTemplates.f_cpu_issue_body),
                                             [MurphiTokens.k_obj_set, str(arch)]) + self.nl

        return exec_str

    def gen_cpu_issue_func(self, exec_str: str):
        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_cpu_issue_head),
                                    [exec_str]) + self.nl

