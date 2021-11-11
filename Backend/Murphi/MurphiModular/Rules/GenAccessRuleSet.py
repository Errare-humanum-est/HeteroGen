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
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess

from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Murphi.BaseConfig import BaseConfig

from Backend.Murphi.MurphiModular.General.GenAtomicEvent import AtomicEvent

from Debug.Monitor.ClassDebug import Debug


class GenAccessRuleSet(TemplateHandler, Debug):

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        TemplateHandler.__init__(self)
        Debug.__init__(self)

        # If litmus testing is activated then access rules must not to be generated
        ruleset_str_list = []

        for cluster in clusters:
            machines = set(cluster.system_tuple)

            for arch in set([machine.arch for machine in machines]):
                ruleset_str = self.gen_access_rules_str(arch, config)
                if not ruleset_str:
                    continue
                ruleset_str = self.rule_set_body(arch, ruleset_str) + self.nl
                ruleset_str_list.append(ruleset_str)

        murphi_str.append("----" + __name__.replace('.','/') + self.nl + self.add_tabs("".join(ruleset_str_list), 1))

    def gen_access_rules_str(self, arch: FlatArchitecture, config: BaseConfig):
        access_rules_str = ""
        state_transition_dict: Dict = {}

        for transition in arch.get_architecture_transitions():
            if isinstance(transition.guard, (BaseAccess.Access, BaseAccess.Evict)):
                if transition.start_state not in state_transition_dict:
                    state_transition_dict[transition.start_state] = MultiDict()
                state_transition_dict[transition.start_state][transition.guard] = transition

        for state in sorted(state_transition_dict.keys(), key=lambda x: str(x)):
            for guard in state_transition_dict[state]:

                # In litmus test cases accesses are handled through traces
                if config.litmus_testing and isinstance(guard, BaseAccess.Access):
                    continue

                # Evicts disabled by configuration flag
                if not config.enable_evicts and isinstance(guard, BaseAccess.Evict):
                    continue

                access_rules_str += self.gen_access_rule(arch, state_transition_dict[state][guard], config) + self.nl
        return access_rules_str

    def gen_access_rule(self, arch: FlatArchitecture, transitions: List[Transition_v2], config: BaseConfig) -> str:
        aux_checks_str = ""
        lock_func_str = ""

        # Check if the network is free and can accept messages
        if self.check_out_msg(transitions):
            aux_checks_str += '& ' + MurphiTokens.f_network_ready + " "

        if config.atomic_events:
            if AtomicEvent().check_atomic_event(arch, transitions):
                aux_checks_str += '& ' + AtomicEvent().gen_test_atomic_event_func(arch)
                lock_func_str += AtomicEvent().gen_lock_atomic_event_func(arch)

        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_access_rule),
                                    [
                                        str(arch) + "_" + str(transitions[0].start_state),
                                        str(transitions[0].guard),
                                        MurphiTokens.v_cbe,
                                        MurphiTokens.k_access_func,
                                        aux_checks_str,
                                        lock_func_str
                                    ]) + self.nl

    @staticmethod
    def check_out_msg(transitions: List[Transition_v2]):
        for transition in transitions:
            if transition.out_msg:
                return True
        return False

    def rule_set_body(self, arch: FlatArchitecture, rules_str: str):
        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_access_rule_set),
                                    [
                                        MurphiTokens.k_obj_set,
                                        str(arch),
                                        MurphiTokens.v_cbe,
                                        MurphiTokens.k_instance,
                                        MurphiTokens.v_cache_block,
                                        rules_str
                                    ]) + self.nl



