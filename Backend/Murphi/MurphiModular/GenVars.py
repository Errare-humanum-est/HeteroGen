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

from Parser.DataTypes.ClassBaseNetwork import Channel

from Backend.Murphi.BaseConfig import BaseConfig
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates


class GenVars(TemplateHandler):

    var_type = "var"

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        TemplateHandler.__init__(self)

        var_str = "--" + __name__.replace('.','/') + self.nl

        var_str += self.gen_network(clusters, config)
        var_str += self.gen_access(config)
        var_str += self.gen_machine_instances(clusters)

        var_str += self.gen_litmus_cpu_var(config)

        murphi_str.append(self.add_tabs(self.var_type + self.nl + self.add_tabs(var_str, 1) + self.nl, 1))

    def gen_network(self, clusters: List[Cluster], config: BaseConfig) -> str:
        network_str = ""
        fifo_str = ""

        for cluster in clusters:
            for global_arch in cluster.get_global_architectures():
                for ordered_network in global_arch.network.ordered_networks:
                    network_str += self.gen_ordered_network(global_arch.network.ordered_networks[ordered_network])
                    if config.enable_fifo:
                        fifo_str += self.gen_fifo(global_arch.network.ordered_networks[ordered_network])
                for unordered_network in global_arch.network.unordered_networks:
                    network_str += self.gen_unordered_network(global_arch.network.unordered_networks[
                                                                  unordered_network])
                    if config.enable_fifo:
                        fifo_str += self.gen_fifo(global_arch.network.unordered_networks[unordered_network])
        return network_str + self.nl + fifo_str + self.nl

    def gen_ordered_network(self, ordered_network: Channel) -> str:
        o_net = self.tab + str(ordered_network) + ": " + MurphiTokens.k_net + MurphiTokens.k_ordered + self.end
        o_net += (self.tab + MurphiTokens.k_vector_cnt + str(ordered_network) + ": " +
                  MurphiTokens.k_net + MurphiTokens.k_ordered_cnt + self.end)
        return o_net

    def gen_unordered_network(self, unordered_network: Channel) -> str:
        return self.tab + str(unordered_network) + ": " + MurphiTokens.k_net + MurphiTokens.k_unordered + self.end

    def gen_fifo(self, network: Channel) -> str:
        return str(self.tab + MurphiTokens.k_buffer + str(network) + ": " +
                   MurphiTokens.k_net + MurphiTokens.k_fifo + self.end)

    def gen_access(self, config: BaseConfig):
        access_str = self.tab + self._stringReplKeys(self._openTemplate(MurphiTemplates.f_perm_var), [MurphiTokens.k_perm_type]) \
               + self.nl
        if config.enable_read_write_execution and not config.litmus_testing:
            access_str += self.tab + self._openTemplate(MurphiTemplates.f_store_monitor_var) + self.nl
        return access_str

    def gen_machine_instances(self, clusters: List[Cluster]) -> str:
        arch_inst_str = ""
        for cluster in clusters:
            archs = set(machine.arch for machine in cluster.system_tuple)
            for arch in archs:
                arch_inst_str += (self.tab + MurphiTokens.k_instance + str(arch) + ": " +
                                  MurphiTokens.k_object + str(arch) + self.end)

        return arch_inst_str

    def gen_litmus_cpu_var(self, config: BaseConfig) -> str:
        if config.litmus_testing:
            return self.nl + self.tab + "i_cpu: OBJ_CPU" + self.end + self.nl
        return ""
