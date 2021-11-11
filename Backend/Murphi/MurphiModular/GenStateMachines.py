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

from Backend.Murphi.MurphiModular.StateMachines.GenMessageStateMachines import GenMessageStateMachines
from Backend.Murphi.MurphiModular.StateMachines.GenAccessStateMachines import GenAccessStateMachines
from Backend.Murphi.MurphiModular.LitmusTestFunc.GenCPULitmusAccessCache import GenCPULitmusAccessCache
from Backend.Murphi.MurphiModular.LitmusTestFunc.GenCPULitmusServeCPU import GenCPULitmusServeCPU

from Backend.Common.TemplateHandler.TemplateBase import TemplateBase
from Backend.Murphi.BaseConfig import BaseConfig


class GenStateMachines(TemplateBase):

    def __init__(self, murphi_str: List[str],
                 clusters: List[Cluster],
                 config: BaseConfig):
        TemplateBase.__init__(self)

        fsm_str_list: List[str] = []
        # Generate litmus test cpu serving functions
        GenCPULitmusServeCPU(fsm_str_list, clusters, config)
        # Generate access message generation procedures
        GenAccessStateMachines(fsm_str_list, clusters, config)
        # Generate litmus test cpu access functions
        GenCPULitmusAccessCache(fsm_str_list, clusters, config)
        # Generate message handling state machine
        GenMessageStateMachines(fsm_str_list, clusters, config)

        fsm_str = "".join(fsm_str_list)

        # Add tabs to support sublime section hiding
        fsm_str = "--" + __name__.replace('.','/') + self.nl + self.nl + self.add_tabs(fsm_str, 1) + self.nl

        murphi_str.append(fsm_str)

