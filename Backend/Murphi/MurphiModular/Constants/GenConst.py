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

from Backend.Murphi.BaseConfig import BaseConfig
from Backend.Murphi.MurphiModular.Constants.GenLitmusConst import GenLitmusConst
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates

from Debug.Monitor.ClassDebug import Debug


class GenConst(TemplateHandler, Debug):

    cadrcnt = 1
    cvalmax = 1

    # Config Parameters
    cfifomax = 1
    enableFifo = 0
    corderedsz = cadrcnt * 3 * 2
    cunorderedsz = cadrcnt * 3 * 2

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        TemplateHandler.__init__(self)
        Debug.__init__(self)

        murphi_str.append(self.gen_license_str())

        const_str = self.gen_static_const_str(config)
        const_str += self.gen_network_const_str(config)
        const_str += self.gen_dyn_const_str(clusters)

        const_str = self.add_tabs(const_str, 1)
        const_str = "--" + __name__.replace('.','/') + self.nl + const_str

        murphi_str.append(const_str)

        # Litmus testing constants
        GenLitmusConst(murphi_str, config)

    def gen_license_str(self):
        return self._openTemplate(MurphiTemplates.f_license) + self.nl

    def gen_static_const_str(self, config: BaseConfig):
        const_str = "---- System access constants" + self.nl
        const_str += self._stringReplKeys(self._openTemplate(MurphiTemplates.f_const),
                                          ["true" if config.enable_fifo else "false"])

        const_str += self.tab + MurphiTokens.c_val_cnt_const + ": " + str(config.c_val_max) + self.end
        const_str += self.tab + MurphiTokens.c_adr_cnt_const + ": " + str(config.c_adr_max) + self.end  # scalarset
        const_str += self.nl

        return const_str

    def gen_network_const_str(self, config: BaseConfig):
        const_str = "---- System network constants" + self.nl
        const_str += self.tab + MurphiTokens.c_ordered_const + ": " + str(config.c_ordered_cnt) + self.end
        const_str += self.tab + MurphiTokens.c_unordered_const + ": " + str(config.c_unordered_cnt) + self.end
        const_str += self.nl

        return const_str

    def gen_dyn_const_str(self, clusters: List[Cluster]):
        const_str = "---- SSP declaration constants" + self.nl

        for cluster in clusters:
            for global_arch in cluster.get_global_architectures():
                for constant_name in global_arch.constants.const_dict:
                    const_val = str(global_arch.constants.const_dict[constant_name])
                    self.perror("Constant definition is not integer", const_val.isdigit())
                    const_str += self.tab + constant_name + ": " + const_val + self.end

        const_str += self.nl

        return const_str


