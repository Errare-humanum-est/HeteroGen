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

from typing import List, Tuple

from DataObjects.ClassCluster import Cluster

from Backend.Murphi.BaseConfig import BaseConfig
from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens

from Debug.Monitor.ClassDebug import Debug


class GenNetworkRule(TemplateHandler, Debug):

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        TemplateHandler.__init__(self)
        Debug.__init__(self)

        self.config = config

        ruleset_str_list = []

        architecture_list, ordered_net_list, unordered_net_list = self.get_machine_networks_list(clusters)

        ruleset_str_list.append(self.gen_fifo_rules(ordered_net_list + unordered_net_list, architecture_list))
        ruleset_str_list.append(self.gen_ordered_network_ruleset(ordered_net_list, architecture_list, config))
        ruleset_str_list.append(self.gen_unordered_network_ruleset(unordered_net_list, architecture_list))

        murphi_str.append("----" + __name__.replace('.','/') + self.nl + self.add_tabs("".join(ruleset_str_list), 1))

    def get_machine_networks_list(self, clusters: List[Cluster]) -> Tuple[List[str], List[str], List[str]]:
        machine_set = set()
        ordered_network_set = set()
        unordered_network_set = set()

        # Generate a list of all machines and networks
        for cluster in clusters:
            machine_set.update(set([str(machine) for machine in cluster.system_tuple]))

            for global_arch in cluster.get_global_architectures():
                ordered_network_set.update(global_arch.network.ordered_networks.keys())
                unordered_network_set.update(global_arch.network.unordered_networks.keys())

        self.perror("Ordered and unordered networks have identical identifiers",
                    not ordered_network_set.intersection(unordered_network_set))

        return list(machine_set), list(ordered_network_set), list(unordered_network_set)

    def gen_fifo_rules(self, network_list: List[str], architecture_list: List[str]) -> str:

        if not self.config.enable_fifo:
            return ""

        ruleset_str_list = []
        for network in network_list:
            ruleset_str_list.append(self.gen_fifo_rule(str(network), architecture_list))

        return "".join(ruleset_str_list) + self.nl

    def gen_fifo_rule(self, network_name: str, archs: List[str]) -> str:
        cond_rule_str = self.gen_cond_rule_part(self.gen_if_elif_structure(archs),
                                                MurphiTokens.k_buffer + network_name,
                                                MurphiTemplates.f_fifo_inner_rule)

        cond_rule_str = self.add_tabs(cond_rule_str, 5)
        inputstr = self._openTemplate(MurphiTemplates.f_fifo_ruleset)
        replacekeys = [MurphiTokens.k_buffer + network_name, cond_rule_str]

        for ind in range(0, len(replacekeys)):
            inputstr = self._stringRepl(inputstr, ind, replacekeys[ind])

        return inputstr + self.nl

    def gen_ordered_network_ruleset(self,
                                    ordered_network_list: List[str],
                                    architecture_list: List[str],
                                    config: BaseConfig) -> str:
        ruleset_str_list = []
        for network_str in ordered_network_list:
            cond_rule_str = self.gen_network_rules(network_str, architecture_list,
                                                   MurphiTemplates.f_ordered_rule_fifo,
                                                   MurphiTemplates.f_ordered_rule_inner)

            # Total order network or point to point ordered network
            ord_net_func = MurphiTemplates.f_total_ordered_rule
            if not config.enable_total_order_network:
                ord_net_func = MurphiTemplates.f_ordered_rule

            ruleset_str_list.append(self._stringReplKeys(self._openTemplate(ord_net_func),
                                                         [network_str, MurphiTokens.k_vector_cnt, cond_rule_str])
                                    + self.nl + self.nl)

        return "".join(ruleset_str_list)

    def gen_unordered_network_ruleset(self, unordered_network_list: List[str], architecture_list: List[str]) -> str:
        ruleset_str_list = []
        for network_str in unordered_network_list:
            cond_rule_str = self.gen_network_rules(network_str, architecture_list,
                                                   MurphiTemplates.f_unordered_rule_fifo,
                                                   MurphiTemplates.f_unordered_rule_inner)

            ruleset_str_list.append(self._stringReplKeys(self._openTemplate(MurphiTemplates.f_unordered_rule),
                                                         [network_str, cond_rule_str]) + self.nl + self.nl)

        return "".join(ruleset_str_list)

    def gen_network_rules(self, network_str: str,
                          architecture_list: List[str],
                          fifo_rule: str,
                          cond_rule: str):
        if self.config.enable_fifo:
            cond_rule_str = self._stringReplKeys(self._openTemplate(fifo_rule), [network_str, MurphiTokens.k_buffer])
        else:
            cond_rule_str = self.gen_cond_rule_part(self.gen_if_elif_structure(architecture_list), network_str,
                                                    cond_rule)
            cond_rule_str += self._openTemplate(MurphiTemplates.f_no_fifo)

        return self.add_tabs(cond_rule_str, 4)

    @staticmethod
    def gen_if_elif_structure(archs: List[str]) -> List[Tuple[str, str]]:
        cond = []
        for ind in range(0, len(archs)):
            if ind == 0:
                cond.append(('if', str(archs[ind])))
            else:
                cond.append(('elsif', str(archs[ind])))
        return cond

    def gen_cond_rule_part(self, cond_archs: List[Tuple[str, str]], network_name: str, template_name: str):
        cond_str = ""
        for cond_arch in cond_archs:
            # If or elsif statement
            cond_str += cond_arch[0]
            cond_str += " IsMember(dst, " + MurphiTokens.k_obj_set + cond_arch[1] + ") then" + self.nl
            cond_str += self.add_tabs(self._stringReplKeys(self._openTemplate(template_name),
                                                           [MurphiTokens.k_msg_func, cond_arch[1], network_name]), 1)
        return cond_str
