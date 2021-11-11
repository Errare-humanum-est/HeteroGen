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

from Backend.Common.TemplateHandler.TemplateBase import TemplateBase
from Backend.Murphi.MurphiModular.Types.GenAdrDef import GenAdrDef
from Backend.Murphi.MurphiModular.Types.Enums.GenEnums import GenEnums
from Backend.Murphi.MurphiModular.Types.GenMachineSets import GenMachineSets
from Backend.Murphi.MurphiModular.Types.GenCheckTypes import GenCheckTypes
from Backend.Murphi.MurphiModular.Types.GenNetwork import GenNetwork
from Backend.Murphi.MurphiModular.Types.GenFIFO import GenFIFO
from Backend.Murphi.MurphiModular.Types.GenMessage import GenMessage
from Backend.Murphi.MurphiModular.Types.GenMachines import GenMachines
from Backend.Murphi.MurphiModular.Types.GenLitmusCPUSet import GenLitmusCPUSet

from Backend.Murphi.BaseConfig import BaseConfig


class GenTypes(TemplateBase):

    type_decl = "type"

    def __init__(self, murphi_str: List[str],
                 clusters: List[Cluster],
                 config: BaseConfig):
        TemplateBase.__init__(self)

        type_str_list: List[str] = []

        GenAdrDef(type_str_list, config)
        GenEnums(type_str_list, clusters)
        GenMachineSets(type_str_list, clusters)

        GenCheckTypes(type_str_list, clusters,  config)

        # Generate interconnect
        GenMessage(type_str_list, clusters, config)
        GenNetwork(type_str_list, config)
        GenFIFO(type_str_list,  config)
        GenMachines(type_str_list, clusters, config)

        # Generate CPUs in case of Litmus testing
        GenLitmusCPUSet(type_str_list,  config)

        type_str = ''.join(type_str_list)

        # Add tabs to support sublime section hiding
        type_str = self.add_tabs(self.type_decl + self.nl + self.add_tabs(type_str, 1), 1)

        type_str = "--" + __name__.replace('.','/') + self.nl + type_str + self.nl

        # Return type string section
        murphi_str.append(type_str)
