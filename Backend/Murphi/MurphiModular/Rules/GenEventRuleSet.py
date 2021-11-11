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

from typing import List

from DataObjects.ClassCluster import Cluster
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.ClassMultiDict import MultiDict
from DataObjects.FlowDataTypes.ClassEvent import Event, EventAck

from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates
from Backend.Murphi.MurphiModular.General.GenAtomicEvent import AtomicEvent
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Murphi.BaseConfig import BaseConfig

from Debug.Monitor.ClassDebug import Debug


class GenEventRuleSet(TemplateHandler, Debug):

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        TemplateHandler.__init__(self)
        Debug.__init__(self)

        ruleset_str_list: List[str] = []

        for cluster in clusters:
            machines = set(cluster.system_tuple)

            for arch in set([machine.arch for machine in machines]):
                ruleset_str = self.gen_event_rules_str(arch)
                if not ruleset_str:
                    continue
                ruleset_str = self.rule_set_body(arch, ruleset_str) + self.nl
                ruleset_str_list.append(ruleset_str)

                if config.atomic_events:
                    atomic_ruleset_str = self.gen_event_atomic_rules_str(arch)
                    ruleset_str_list.append(self.rule_set_body(arch, atomic_ruleset_str) + self.nl)

            murphi_str.append("----" + __name__.replace('.','/') + self.nl + self.add_tabs("".join(ruleset_str_list), 1))

    def gen_event_rules_str(self, arch: FlatArchitecture) -> str:
        event_rules_str = ""
        state_transition_dict: MultiDict = MultiDict()

        for transition in arch.get_architecture_transitions():
            if isinstance(transition.guard, Event) or isinstance(transition.guard, EventAck):
                state_transition_dict[transition.start_state] = transition

        for state in sorted(state_transition_dict.keys(), key=lambda x: str(x)):
            trans_guard_list = []
            for transition in state_transition_dict[state]:

                if str(transition.guard) in trans_guard_list:
                    continue

                trans_guard_list.append(str(transition.guard))

                # Remote events
                if isinstance(transition.guard, Event):
                    event_rules_str += self.gen_event_rule(arch, transition, MurphiTemplates.f_remote_event_rule) \
                                       + self.nl

                # Init event completion
                if isinstance(transition.guard, EventAck):
                    event_rules_str += self.gen_event_rule(arch, transition, MurphiTemplates.f_init_event_rule) \
                                       + self.nl

        return event_rules_str

    def gen_event_rule(self,
                       arch: FlatArchitecture,
                       transition: Transition_v2,
                       evt_func: str) -> str:
        return self._stringReplKeys(self._openTemplate(evt_func),
                                    [
                                        str(arch) + "_" + str(transition.start_state),
                                        str(transition.guard),
                                        MurphiTokens.v_cbe,
                                        str(arch),
                                        MurphiTokens.k_access_func,
                                        '& ' + MurphiTokens.f_network_ready if transition.out_msg else ''
                                    ]) + self.nl

    def rule_set_body(self, arch: FlatArchitecture, rules_str: str) -> str:
        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_access_rule_set),
                                    [
                                        MurphiTokens.k_obj_set,
                                        str(arch),
                                        MurphiTokens.v_cbe,
                                        MurphiTokens.k_instance,
                                        MurphiTokens.v_cache_block,
                                        rules_str
                                    ]) + self.nl

    def gen_event_atomic_rules_str(self, arch: FlatArchitecture) -> str:
        atomic_unlock_str = ""
        for state in arch.stable_states:
            atomic_unlock_str += self.gen_atomic_unlock(arch, state)

        return atomic_unlock_str

    def gen_atomic_unlock(self, arch: FlatArchitecture, state: State_v2) -> str:
        return self._stringReplKeys(self._openTemplate(AtomicEvent.f_atomic_event_ruleset_template),
                                    [
                                        str(arch),
                                        str(state),
                                        AtomicEvent.unlock_atomic_event_func,
                                        MurphiTokens.v_cbe
                                    ]) + self.nl

