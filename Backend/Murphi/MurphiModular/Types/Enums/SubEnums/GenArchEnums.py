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

from typing import List, Dict, Any

from DataObjects.ClassCluster import Cluster
from DataObjects.States.ClassStatev2 import State_v2

from Backend.Common.TemplateHandler.TemplateBase import TemplateBase
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Debug.Monitor.ClassDebug import Debug


class GenArchEnums(TemplateBase, Debug):

    def __init__(self, murphi_str: List[str], clusters: List[Cluster]):
        TemplateBase.__init__(self)
        Debug.__init__(self)

        state_enum_str = "------" + __name__.replace('.', '/') + self.nl

        for cluster in clusters:
            for arch in cluster.get_machine_architectures():
                # Generate states
                state_enum_str += self.gen_state_enums(str(arch), arch.get_architecture_states_verified())
                # Generate events
                state_enum_str += self.gen_event_enums(str(arch), arch.event_network.event_issue)

        murphi_str.append(state_enum_str)

    def gen_state_enums(self, arch: str, state_list: List[State_v2]) -> str:

        state_str = MurphiTokens.k_state_label + str(arch) + ": enum {" + self.nl
        state_str_list = [str(state) for state in state_list]

        self.pwarning("Duplicated state identifiers found in architecture: " + str(state_str_list),
                      len(state_str_list) != len(set(state_str_list)))

        for state in sorted(list(set(state_str_list)), key=lambda x: str(x), reverse=True):
            state_str += self.tab + str(arch) + "_" + str(state) + "," + self.nl

        state_str = state_str[:state_str.rfind(",")]
        return state_str + self.nl + "}" + self.end + self.nl

    def gen_event_enums(self, arch: str, event_dict: Dict[str, Any]) -> str:
        if not event_dict:
            return ""

        state_str = MurphiTokens.k_event_label + str(arch) + ": enum {" + self.nl
        for event in event_dict:
            state_str += self.tab + str(arch) + "_" + str(event) + "," + self.nl

        state_str = state_str[:state_str.rfind(",")]
        return state_str + self.nl + "}" + self.end + self.nl
