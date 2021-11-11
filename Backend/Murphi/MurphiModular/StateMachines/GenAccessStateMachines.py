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

from typing import List, Dict, Any

from DataObjects.ClassCluster import Cluster
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.ClassMultiDict import MultiDict
from DataObjects.FlowDataTypes.ClassEvent import Event, EventAck

from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess

from Backend.Common.TemplateHandler.TemplateBase import TemplateBase
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Murphi.BaseConfig import BaseConfig
from Backend.Murphi.MurphiModular.Types.GenMachineEntry import GenMachineEntry
from Backend.Murphi.MurphiModular.General.GenMurphiTree import GenMurphiRevTree

from Backend.Common.GenTokenSequenceFromTree import TokenSequenceFromTree
from Backend.Common.GenPCCToTarget import GenPCCToTarget

from Debug.Monitor.ClassDebug import Debug


class GenAccessStateMachines(TemplateBase):

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        TemplateBase.__init__(self)

        self.arch_type_dict: Dict[FlatArchitecture, GenMachineEntry] = {}
        self.config = config

        access_fsm_str_list = []

        for cluster in clusters:
            machines = set(cluster.system_tuple)

            for arch in sorted(set([machine.arch for machine in machines]), key=lambda x: str(x)):
                access_fsm_str_list.append(self.gen_state_machine_graph(cluster, arch, config))

        murphi_str.append("----" + __name__.replace('.', '/') + self.nl + "".join(access_fsm_str_list))

    def gen_state_machine_graph(self, cluster: Cluster, arch: FlatArchitecture, config: BaseConfig) -> str:
        state_case_str = ""
        state_transition_token_list_dict = {}

        for start_state in arch.stable_states:
            for sub_tree in arch.state_sub_tree_dict[start_state]:
                for state, value in TokenSequenceFromTree(sub_tree).state_operation_seq_dict.items():
                    if state not in state_transition_token_list_dict:
                        state_transition_token_list_dict[state] = {}
                    state_transition_token_list_dict[state].update(value)

        for state in sorted(state_transition_token_list_dict.keys(), key=lambda x: str(x)):
            state_case_str += self._gen_state_access_statement(cluster, arch, config, state,
                                                               state_transition_token_list_dict[state])

        return self.add_tabs(state_case_str, 1)

    def _gen_state_access_statement(self, cluster: Cluster, arch: FlatArchitecture, config: BaseConfig,
                                    state: State_v2, transition_token_dict):
        access_str = ""
        for guard in sorted(transition_token_dict.keys(), key=lambda x: str(x)):
            if (isinstance(guard, BaseAccess.Access_type)
                    or isinstance(guard, Event) or isinstance(guard, EventAck)):

                pcc_to_target = GenPCCToTarget(cluster, arch, config)
                ret_target_list = [pcc_to_target.gen_operation(operation) for operation in transition_token_dict[guard]]
                Debug.perror(f"PCC could not be correctly translated to target: {ret_target_list}",
                             None not in ret_target_list)

                access_func_str = self.add_tabs("".join(ret_target_list), 1)
                access_str += (self._gen_access_func_header(arch, state, guard, pcc_to_target) +
                               access_func_str +
                               self._gen_access_func_end()) + self.nl
        return access_str

    def _gen_access_func_header(self, arch: FlatArchitecture, start_state: State_v2, guard,
                                pcc_to_target: GenPCCToTarget) -> str:

        fct_header = "procedure " + MurphiTokens.k_access_func + str(arch) + "_" + str(start_state) + "_" + \
                     str(guard) + \
                     "(" + MurphiTokens.v_adr + ":" + MurphiTokens.k_address + "; " + MurphiTokens.v_mach + ":" \
                     + MurphiTokens.k_obj_set + str(arch) + \
                     ")" + self.end
        fct_header += pcc_to_target.gen_local_variables()

        fct_header += "begin" + self.nl
        fct_header += "alias " + MurphiTokens.v_cbe + ": " + MurphiTokens.k_instance + str(arch) + \
                      "[" + MurphiTokens.v_mach + "]." + MurphiTokens.v_cache_block + "[" + MurphiTokens.v_adr \
                      + "] do" + self.nl
        return fct_header

    def _gen_access_func_end(self) -> str:
        fct_end = "endalias" + self.end
        fct_end += MurphiTokens.k_end + self.end
        return fct_end
