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

from Parser.DataTypes.ClassBaseNetwork import BaseMessage

from DataObjects.ClassCluster import Cluster
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.ClassMultiDict import MultiDict

from Backend.Common.TemplateHandler.TemplateBase import TemplateBase
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Murphi.BaseConfig import BaseConfig
from Backend.Murphi.MurphiModular.Types.GenMachineEntry import GenMachineEntry
from Backend.Murphi.MurphiModular.General.GenMurphiTree import GenMurphiRevTree
from Backend.Murphi.MurphiModular.General.GenAtomicEvent import AtomicEvent
from Debug.Monitor.ClassDebug import Debug


class GenMessageStateMachines(TemplateBase, Debug):

    k_operation = "operation"
    k_final_state = "final_state"

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        TemplateBase.__init__(self)
        Debug.__init__(self)

        self.arch_type_dict: Dict[FlatArchitecture, GenMachineEntry] = {}
        self.arch_local_var_dict: Dict[FlatArchitecture, GenMurphiRevTree] = {}
        self.config = config

        fsm_msg_str_list = []

        for cluster in clusters:
            machines = set(cluster.system_tuple)

            for arch in set([machine.arch for machine in machines]):
                self.arch_local_var_dict[arch] = GenMurphiRevTree(cluster, arch, config, True)
                func_str = (self.gen_state_machine_graph(arch))
                fsm_msg_str_list.append(self._gen_mach_func_header(arch) + func_str + self._gen_mach_func_end()
                                        + self.nl)

        murphi_str.append("----" + __name__.replace('.','/') + self.nl + self.add_tabs("".join(fsm_msg_str_list), 1))

    def gen_state_machine_graph(self, arch: FlatArchitecture) -> str:
        state_case_str = ""
        state_transition_dict: MultiDict = MultiDict()

        for transition in arch.get_architecture_transitions():
            state_transition_dict[str(transition.start_state)] = transition

        for state in sorted(state_transition_dict.keys(), key=lambda x: str(x)):
            state_case_str += self._gen_case_str(str(arch) + "_" + str(state))
            state_case_str += self._gen_switch_str(MurphiTokens.v_in_msg + "." + MurphiTokens.v_m_type)


            state_case_str += self.add_tabs(
                self.gen_state_case_statement(arch, state_transition_dict[state]), 1)
            state_case_str += self.add_tabs(self._gen_else_case_str(), 1)
            state_case_str += self._gen_end_switch_str() + self.nl

        return self.add_tabs(state_case_str, 1)

    def gen_state_case_statement(self, arch: FlatArchitecture, transitions: List[Transition_v2]) -> str:
        msg_case_str = ""
        transition_guard_dict: MultiDict = MultiDict()

        for transition in transitions:
            if isinstance(transition.guard, BaseMessage) and str(transition.guard) \
                    in arch.global_arch.network.base_message_dict:
                transition_guard_dict[str(transition.guard)] = transition

        for guard in sorted(transition_guard_dict.keys(), key=lambda x: str(x)):
            msg_case_str += self._gen_case_str(str(guard))
            msg_case_str += self.gen_atomic_event_check(arch, transition_guard_dict[guard])
            msg_case_str += self.add_tabs(
                self.arch_local_var_dict[arch].gen_murphi_tree(transition_guard_dict[guard]), 1) + self.nl

        return msg_case_str

    def gen_atomic_event_check(self, arch: FlatArchitecture, transitions: List[Transition_v2]) -> str:
        aux_checks_str = ""
        if self.config.atomic_events and transitions and transitions[0].start_state in arch.state_sub_tree_dict:
            true_test = [True for transition in transitions if AtomicEvent().check_atomic_event(arch, transition)]
            if true_test:
                aux_checks_str += "if " + AtomicEvent().gen_test_atomic_event_func(arch) + " then" + self.nl
                aux_checks_str += self.tab + AtomicEvent().gen_lock_atomic_event_func(arch) + self.nl
                aux_checks_str += self._gen_else_case_str()
                aux_checks_str += "endif" + self.end
        return aux_checks_str

    def _gen_mach_func_header(self, arch: FlatArchitecture) -> str:
        fct_header = "function " + MurphiTokens.k_msg_func + str(arch) + \
                    "(" + MurphiTokens.v_in_msg + ":" + MurphiTokens.k_message + "; " \
                     + MurphiTokens.v_mach + ":" + MurphiTokens.k_obj_set + str(arch) \
                     + ") : boolean" + self.end
        fct_header += self.arch_local_var_dict[arch].gen_local_variables()

        fct_header += "begin" + self.nl
        fct_header += self.tab + "alias " + MurphiTokens.v_adr + ": " + MurphiTokens.v_in_msg \
                      + "." + MurphiTokens.v_adr + " do" + self.nl
        fct_header += self.tab + "alias " + MurphiTokens.v_cbe + ": " + MurphiTokens.k_instance + str(arch) + \
                     "[" + MurphiTokens.v_mach + "]." + MurphiTokens.v_cache_block + "[" + MurphiTokens.v_adr + "] do" \
                     + self.nl
        fct_header += "switch " + MurphiTokens.v_cbe + "." + MurphiTokens.k_state + self.nl
        return fct_header

    def _gen_mach_func_end(self) -> str:
        fct_end = self._gen_end_switch_str()
        fct_end += "endalias" + self.end
        fct_end += "endalias" + self.end
        fct_end += "return false" + self.end
        fct_end += MurphiTokens.k_end + self.end
        return fct_end

    def _gen_case_str(self, guard: str) -> str:
        return MurphiTokens.k_case + " " + guard + ":" + self.nl

    def _gen_else_case_str(self) -> str:
        return "else return false" + self.end

    def _gen_switch_str(self, switch: str) -> str:
        return MurphiTokens.k_switch + " " + switch + self.nl

    def _gen_end_switch_str(self) -> str:
        return MurphiTokens.k_end_switch + self.end
