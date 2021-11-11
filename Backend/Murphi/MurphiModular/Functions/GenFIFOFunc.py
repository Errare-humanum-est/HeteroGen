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

from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates
from Backend.Murphi.BaseConfig import BaseConfig

from DataObjects.ClassCluster import Cluster

from Debug.Monitor.ClassDebug import Debug


class GenFIFOFunc(TemplateHandler, Debug):

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        TemplateHandler.__init__(self)
        Debug.__init__(self)

        fifo_str = "----" + __name__.replace('.','/') + self.nl
        if config.enable_fifo:
            fifo_str += self.add_tabs(self._stringReplKeys(self._openTemplate(MurphiTemplates.f_fifo_func),
                                                           [
                                                               str(config.c_fifo_max),
                                                               MurphiTokens.k_net,
                                                               MurphiTokens.k_machines,
                                                               MurphiTokens.k_message
                                                           ]), 1) + self.nl + self.nl

            fifo_str += self.add_tabs(self._stringReplKeys(self._openTemplate(MurphiTemplates.f_fifo_reset_body),
                                                           [
                                                               MurphiTokens.k_buffer,
                                                               self.gen_fifo_reset_func(clusters)
                                                           ]), 1) + self.nl + self.nl

        murphi_str.append(fifo_str)

    def gen_fifo_reset_func(self, clusters: List[Cluster]):
        fifo_cond_str = ""
        network_set = set()

        for cluster in clusters:
            for arch in cluster.get_machine_architectures():
                network_set.update({**arch.global_arch.network.ordered_networks,
                                    **arch.global_arch.network.unordered_networks})

        for network in network_set:
            fifo_cond_str += self.add_tabs(self._stringReplKeys(self._openTemplate(MurphiTemplates.f_fifo_reset_inner),
                                                                [str(network), MurphiTokens.k_buffer]), 1) + self.nl

        return fifo_cond_str


