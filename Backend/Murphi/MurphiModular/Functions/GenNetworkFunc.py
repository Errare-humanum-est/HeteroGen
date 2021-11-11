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

from typing import List, Set, Tuple

from DataObjects.ClassCluster import Cluster
from DataObjects.ClassMultiDict import MultiDict

from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates
from Backend.Murphi.BaseConfig import BaseConfig

from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from Parser.DataTypes.ClassBaseNetwork import Channel

from Backend.Murphi.MurphiModular.General.GenPCCToMurphi import GenPCCToMurphi

from Debug.Monitor.ClassDebug import Debug


class GenNetworkFunc(TemplateHandler, Debug):

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        TemplateHandler.__init__(self)
        Debug.__init__(self)

        network_str = ""

        network_str += self.gen_ordered_send_func(clusters, config)
        network_str += self.gen_unordered_send_func(clusters)

        # Generate Multicast functions if they exist
        network_str += self.gen_multicast_func(clusters)

        # Generate Broadcast functions if they exist
        network_str += self.gen_broadcast_func(clusters)

        # Generate the network ready check functions
        network_str += self.gen_network_ready_func(clusters, config)

        # Generate the network reset functions
        network_str += self.gen_network_reset(clusters, config)

        murphi_str.append("----" + __name__.replace('.','/') + self.nl + self.add_tabs(network_str, 1) + self.nl)

    def gen_ordered_send_func(self, clusters: List[Cluster], config: BaseConfig):
        network_str = ""
        for cluster in clusters:
            for global_arch in cluster.get_global_architectures():

                # Total order network or point to point ordered network
                ord_net_func = MurphiTemplates.f_total_ordered_network_func
                if not config.enable_total_order_network:
                    ord_net_func = MurphiTemplates.f_ordered_network_func

                for ordered_network in global_arch.network.ordered_networks:
                    network_str += self._stringReplKeys(self._openTemplate(ord_net_func),
                                                        [str(ordered_network),
                                                         MurphiTokens.k_vector_cnt,
                                                         MurphiTokens.c_ordered_const,
                                                         MurphiTokens.k_machines]) \
                                   + self.nl + self.nl
        return network_str

    def gen_unordered_send_func(self, clusters: List[Cluster]):
        network_str = ""
        for cluster in clusters:
            for global_arch in cluster.get_global_architectures():
                for unordered_network in global_arch.network.unordered_networks:
                    network_str += self._stringReplKeys(self._openTemplate(MurphiTemplates.f_unordered_network_func),
                                                        [str(unordered_network),
                                                         MurphiTokens.c_unordered_const,
                                                         MurphiTokens.k_machines]) \
                                   + self.nl + self.nl
        return network_str

    ## Generate multicast functions
    # @param clusters A list of clusters which create the system
    def gen_multicast_func(self, clusters: List[Cluster]) -> str:
        multicast_str_list: List[str] = []
        for cluster in clusters:
            multicast_str_list.append(self._multicast_gen_level(cluster))
        return ''.join(multicast_str_list)

    def _multicast_gen_level(self, cluster: Cluster) -> str:
        multicast_str_list: List[str] = []

        for arch in cluster.get_machine_architectures():
            # Dict[variable_str, network_str]
            multi_cast_dict = MultiDict()

            transitions = arch.get_architecture_transitions()

            for transition in transitions:
                for operation in transition.operations:
                    children = operation.getChildren()
                    if str(operation) == ProtoParserBase.k_mcast:
                        self.perror("Message assigned to unknown network",
                                    str(children[0]) in arch.global_arch.network.unordered_networks or
                                    str(children[0]) in arch.global_arch.network.ordered_networks)
                        multi_cast_dict[str(children[0])] = str(children[2])

            self._multicast_func_gen(multicast_str_list, multi_cast_dict, cluster)

        return ''.join(multicast_str_list)

    def _multicast_func_gen(self, multicast_str_list: List[str], multi_cast_dict: MultiDict, cluster: Cluster):
        for network_name in multi_cast_dict:
            var_defs = set(multi_cast_dict[network_name])
            for var_def in var_defs:
                multicast_str_list.append(
                    self._stringReplKeys(self._openTemplate(MurphiTemplates.f_multicast_network_func),
                                                               [network_name,
                                                                GenPCCToMurphi().gen_vector(var_def),
                                                                GenPCCToMurphi().gen_vector(var_def),
                                                                MurphiTokens.k_machines])
                    + self.nl + self.nl)

    ## Generate broadcast functions
    # @param A broadcast is only possible within the cluster
    def gen_broadcast_func(self, clusters: List[Cluster]) -> str:
        broadcast_str_list: List[str] = []
        for cluster in clusters:
            broadcast_str_list.append(self._broadcast_gen_cluster(cluster))
        # The broadcast must only happen in local cluster
        return "".join(broadcast_str_list)

    def _broadcast_gen_cluster(self, cluster: Cluster) -> str:
        broadcast_str_list: List[str] = []
        arch_set: Set[str] = set()
        # List of networks in cluster that are broadcasting
        broadcast_net_set: Set[str] = set()

        architectures = cluster.get_machine_architectures()
        for arch in architectures:
            transitions = arch.get_architecture_transitions()
            arch_set.add(str(arch))

            for transition in transitions:
                for operation in transition.operations:
                    children = operation.getChildren()
                    if str(operation) == ProtoParserBase.k_bcast:
                        self.perror("Message assigned to unknown network",
                                    str(children[0]) in arch.global_arch.network.unordered_networks or
                                    str(children[0]) in arch.global_arch.network.ordered_networks)
                        broadcast_net_set.add(str(children[0]))

        self._broadcast_func_gen(broadcast_str_list, broadcast_net_set, arch_set, cluster)
        return "".join(broadcast_str_list)

    # Broadcasts are limited to their cluster and cannot directly communicate across clusters
    def _broadcast_func_gen(self,
                            broadcast_str_list: List[str],
                            broadcast_net_set: Set[str],
                            arch_set: Set[str],
                            cluster: Cluster):
        cond_str = self._broadcast_func_cond_gen(arch_set)

        for network_name in broadcast_net_set:
            broadcast_str_list.append(self._stringReplKeys(self._openTemplate(MurphiTemplates.f_broadcast_network_func),
                                                           [network_name,
                                                            cluster.cluster_id,
                                                            cond_str,
                                                            MurphiTokens.k_machines])
                                      + self.nl + self.nl)

    ## Murphi cannot work with unions for IsMember functions, that is why it is necessary to test every set
    #
    def _broadcast_func_cond_gen(self, arch_set: Set[str]):
        arch_list = list(arch_set)
        cond_str = ""
        for ind in range(0, len(arch_list)):
            cond_str += "IsMember(dst, " + MurphiTokens.k_obj_set + arch_list[ind] + ")"
            if ind < len(arch_list)-1:
                cond_str += " | " + self.nl + self._broadcast_if_spacer()
        return cond_str

    def _broadcast_if_spacer(self) -> str:
        ret_tab = ""
        for ind in range(0, 7):
            ret_tab += self.tab
        return ret_tab

    ## Generate the network ready check function
    #
    def gen_network_ready_func(self, clusters: List[Cluster], config: BaseConfig) -> str:
        network_ready_str = ""

        request_networks, networks = self.filter_request_networks_by_channel(clusters)

        network_names: List[str] = []
        subtraction_cnt = config.total_mach_cnt
        # Substituted request network for network. All networks must be ready to serve a response to an issued request
        for network in networks:
            if str(network) in network_names:
                Debug.pwarning("Multiple networks have same name and identifiers. This could potentially lead to "
                               "deadlocks if this was not desired when designing the system")
                continue

            network_names.append(str(network))

            if network.vc_type == network.k_unordered:
                network_ready_str += self._stringReplKeys(self._openTemplate(MurphiTemplates.f_unordered_network_ready_func),
                                                          [str(network), MurphiTokens.c_unordered_const,
                                                           str(subtraction_cnt)]) + self.nl
            else:
                # Total order network or point to point ordered network
                ord_net_func = MurphiTemplates.f_total_ordered_network_ready_func
                if not config.enable_total_order_network:
                    ord_net_func = MurphiTemplates.f_ordered_network_ready_func

                network_ready_str += self._stringReplKeys(self._openTemplate(ord_net_func),
                                                          [str(network), MurphiTokens.k_vector_cnt,
                                                           MurphiTokens.c_ordered_const, str(subtraction_cnt)]) \
                                     + self.nl

        return network_ready_str + self.gen_global_check_network_ready_func(networks) + self.nl

    def gen_global_check_network_ready_func(self, networks: Set[Channel]):
        global_network_ready_inner = ""
        for network in networks:
            global_network_ready_inner += self._stringReplKeys(self._openTemplate(MurphiTemplates.f_network_ready_inner),
                                                               [str(network)]) + self.nl

        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_network_ready_outer),
                                    [global_network_ready_inner]) + self.nl

    @staticmethod
    def filter_request_networks_by_channel(clusters: List[Cluster]) -> Tuple[Set[Channel], Set[Channel]]:
        request_networks: Set[Channel] = set()
        networks: Set[Channel] = set()

        for cluster in clusters:
            for arch in cluster.get_machine_architectures():
                transitions = arch.get_architecture_transitions()

                for transition in transitions:
                    for out_msg in transition.out_msg:
                        networks.add(out_msg.base_msg.vc)
                        if isinstance(transition.guard, BaseAccess.Access_type):
                            request_networks.add(out_msg.base_msg.vc)

        return request_networks, networks

    def gen_network_reset(self, clusters: List[Cluster], config: BaseConfig) -> str:
        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_fifo_reset_body),
                                    [MurphiTokens.k_net, self.gen_network_reset_func(clusters, config)]) \
               + self.nl + self.nl

    def gen_network_reset_func(self, clusters: List[Cluster], config: BaseConfig) -> str:
        ordered_network_set = set()
        unordered_network_set = set()

        # Generate a list of all machines and networks
        for cluster in clusters:

            for global_arch in cluster.get_global_architectures():
                ordered_network_set.update(global_arch.network.ordered_networks.keys())
                unordered_network_set.update(global_arch.network.unordered_networks.keys())

        self.perror("Ordered and unordered networks have identical identifiers",
                    not ordered_network_set.intersection(unordered_network_set))

        return self.add_tabs(self.gen_ordered_network_reset_str(ordered_network_set, config)
                             + self.gen_unordered_network_reset_str(unordered_network_set), 1)

    def gen_ordered_network_reset_str(self, ordered_network_list: Set[str], config: BaseConfig) -> str:
        ordered_network_reset_str = ""

        # Total order network or point to point ordered network
        ord_net_func = MurphiTemplates.f_total_ordered_reset
        if not config.enable_total_order_network:
            ord_net_func = MurphiTemplates.f_ordered_reset

        for ordered_network in ordered_network_list:
            ordered_network_reset_str += self._stringReplKeys(self._openTemplate(ord_net_func),
                                                              [str(ordered_network), MurphiTokens.k_vector_cnt]
                                                              ) + self.nl

        return ordered_network_reset_str

    def gen_unordered_network_reset_str(self, unordered_network_list: Set[str]) -> str:
        unordered_network_reset_str = ""

        for unordered_network in unordered_network_list:
            unordered_network_reset_str += self._stringReplKeys(self._openTemplate(MurphiTemplates.f_unordered_reset),
                                                                [str(unordered_network)]) + self.nl

        return unordered_network_reset_str
