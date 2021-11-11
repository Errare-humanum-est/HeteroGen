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
from Backend.Common.TemplateHandler.TemplateBase import TemplateBase
from Backend.Murphi.BaseConfig import BaseConfig

from Debug.Monitor.ClassDebug import Debug


class GenNetwork(TemplateBase, Debug):

    c_fifo_max = 0

    def __init__(self, murphi_str: List[str], config: BaseConfig):
        TemplateBase.__init__(self)
        Debug.__init__(self)

        fifo_str = "----" + __name__.replace('.','/') + self.nl
        fifo_str += self.add_tabs(self._gen_network_objects(config), 1) + self.nl

        murphi_str.append(fifo_str)

    def _gen_network_objects(self, config: BaseConfig):
        objstr = ""

        point_to_point_ext_str = ""
        if not config.enable_total_order_network:
            point_to_point_ext_str = "] of array[" + MurphiTokens.k_machines

        # Ordered Interconnect
        objstr += (MurphiTokens.k_net + MurphiTokens.k_ordered + ": array[" + MurphiTokens.k_machines
                   + point_to_point_ext_str + "] of array[0.." + MurphiTokens.c_ordered_const + "-1] of "
                   + MurphiTokens.k_message + self.end)

        objstr += (MurphiTokens.k_net + MurphiTokens.k_ordered_cnt + ": array[" + MurphiTokens.k_machines
                   + point_to_point_ext_str + "] of 0.." + MurphiTokens.c_ordered_const + self.end)

        objstr += (MurphiTokens.k_net + MurphiTokens.k_unordered + ": array[" + MurphiTokens.k_machines
                   + "] of multiset[" + MurphiTokens.c_unordered_const + "] of " + MurphiTokens.k_message + self.end)

        return objstr
