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


class GenAccessStateMachines(TemplateBase):

    k_operation = "operation"
    k_final_state = "final_state"

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
        state_transition_dict: MultiDict = MultiDict()
        state_transition_token_list_dict = {}

        for start_state in arch.stable_states:
            for sub_tree in arch.state_sub_tree_dict[start_state]:
                sub_tree_dict = TokenSequenceFromTree(sub_tree).state_operation_seq_dict
                for state, value in TokenSequenceFromTree(sub_tree).state_operation_seq_dict.items():
                    if state not in state_transition_token_list_dict:
                        state_transition_token_list_dict[state] = {}
                    state_transition_token_list_dict[state].update(value)

        for transition in arch.get_architecture_transitions():
            state_transition_dict[transition.start_state] = transition

        for state in sorted(state_transition_dict.keys(), key=lambda x: str(x)):
            state_case_str += self.gen_state_access_statement(cluster, arch, config, state_transition_dict[state])

        return self.add_tabs(state_case_str, 1)

    def gen_state_access_statement(self, cluster: Cluster, arch: FlatArchitecture, config: BaseConfig,
                                   transitions: List[Transition_v2]) -> str:
        access_str = ""
        transition_guard_dict: MultiDict = MultiDict()

        for transition in transitions:
            if (isinstance(transition.guard, BaseAccess.Access_type)
                    or isinstance(transition.guard, Event) or isinstance(transition.guard, EventAck)):
                transition_guard_dict[str(transition.guard)] = transition

        for guard in sorted(transition_guard_dict.keys(), key=lambda x: str(x)):
            # Generate the function body
            murphi_tree = GenMurphiRevTree(cluster, arch, config, False)
            access_func_str = self.add_tabs(murphi_tree.gen_murphi_tree(transition_guard_dict[guard]), 1)

            access_str += (self._gen_access_func_header(arch, transition_guard_dict[guard][0], murphi_tree) +
                           access_func_str +
                           self._gen_access_func_end()) + self.nl
        return access_str

    def _gen_access_func_header(self, arch: FlatArchitecture, transition: Transition_v2,
                                murphi_tree: GenMurphiRevTree) -> str:

        fct_header = "procedure " + MurphiTokens.k_access_func + str(arch) + "_" + str(transition.start_state) + "_" + \
                     str(transition.guard) + \
                     "(" + MurphiTokens.v_adr + ":" + MurphiTokens.k_address + "; " + MurphiTokens.v_mach + ":" \
                     + MurphiTokens.k_obj_set + str(arch) + \
                     ")" + self.end
        fct_header += murphi_tree.gen_local_variables()

        fct_header += "begin" + self.nl
        fct_header += "alias " + MurphiTokens.v_cbe + ": " + MurphiTokens.k_instance + str(arch) + \
                      "[" + MurphiTokens.v_mach + "]." + MurphiTokens.v_cache_block + "[" + MurphiTokens.v_adr \
                      + "] do" + self.nl
        return fct_header

    def _gen_access_func_end(self) -> str:
        fct_end = "endalias" + self.end
        fct_end += MurphiTokens.k_end + self.end
        return fct_end
