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
from DataObjects.FlowDataTypes.ClassEvent import EventAck

from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Common.TemplateHandler.TemplateBase import TemplateBase
from Backend.Murphi.BaseConfig import BaseConfig


class GenResetFunc(TemplateBase):

    def __init__(self, murphi_str: List[str],
                 clusters: List[Cluster],
                 config: BaseConfig):
        TemplateBase.__init__(self)

        # Add tabs to support sublime section hiding
        murphi_str.append("--" + __name__.replace('.','/') + self.nl + self.nl + self.add_tabs(self.gen_base_reset(clusters, config), 1)
                          + self.nl)

    def gen_base_reset(self, clusters: List[Cluster], config: BaseConfig) -> str:
        base_reset_str = "procedure " + MurphiTokens.k_system_reset + "()" + self.end
        base_reset_str += "begin" + self.nl
        base_reset_str += "Reset_perm()" + self.end
        if config.enable_read_write_execution and not config.litmus_testing:
            base_reset_str += "Reset_global_monitor()" + self.end
        base_reset_str += "Reset_" + MurphiTokens.k_net + "()" + self.end

        if config.enable_fifo:
            base_reset_str += "Reset_" + MurphiTokens.k_buffer + "()" + self.end

        base_reset_str += MurphiTokens.k_reset_machines + "()" + self.end

        # Add event reset
        if self.check_event_exist(clusters):
            base_reset_str += MurphiTokens.k_reset_event + "()" + self.end

        # Add litmus cpu init and reset
        if config.litmus_testing:
            base_reset_str += "Litmus_CPU_Init()" + self.end

        base_reset_str += MurphiTokens.k_end + self.end + self.nl

        return base_reset_str

    @staticmethod
    def check_event_exist(clusters: List[Cluster]) -> bool:
        for cluster in clusters:
            for machine in cluster.system_tuple:
                for transition in machine.arch.get_architecture_transitions():
                    if isinstance(transition.guard, EventAck):
                        return True
        return False
