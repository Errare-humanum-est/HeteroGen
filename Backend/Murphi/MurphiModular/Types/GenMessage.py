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
from collections import OrderedDict

from DataObjects.ClassCluster import Cluster

from Backend.Common.TemplateHandler.TemplateBase import TemplateBase
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Murphi.MurphiModular.General.GenDataTypes import GenDataTypes
from Backend.Murphi.BaseConfig import BaseConfig

from Debug.Monitor.ClassDebug import Debug


class GenMessage(GenDataTypes, TemplateBase, Debug):

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        GenDataTypes.__init__(self, MurphiTokens.k_message)
        TemplateBase.__init__(self)
        Debug.__init__(self)

        self.super_type_defs = OrderedDict()

        msg_record_str = MurphiTokens.k_message + ": record" + self.nl

        # Create base msg definition
        for def_pair in MurphiTokens.base_msg:
            msg_record_str += self.tab + def_pair[0] + ": " + def_pair[1] + self.end

        for cluster in clusters:
            for global_arch in cluster.get_global_architectures():
                for msg_type in global_arch.network.msg_types:
                    msg_defs = global_arch.network.msg_types[msg_type].msg_vars

                    for msg_def in msg_defs:
                        if msg_def in self.super_type_defs:
                            if str(msg_defs[msg_def]) != str(self.super_type_defs[msg_def]):
                                self.perror("The variable definitions don't match: " + str(msg_defs[msg_def]) + " | "
                                            + str(self.super_type_defs[msg_def]))
                        else:
                            self.super_type_defs[msg_def] = msg_defs[msg_def]

        for super_type_def in self.super_type_defs:
            # Iterate over data types and convert them to Murphi data types
            msg_record_str += (self.tab + super_type_def + ": " +
                               self.gen_data_type(self.super_type_defs[super_type_def], super_type_def) + self.end)

        msg_record_str += MurphiTokens.k_end + self.end + self.nl

        type_def_str = ""
        for vector_def in self.vector_defs:
            if not config.exist_vector_type(vector_def, self.vector_defs[vector_def]):
                type_def_str += self.vector_defs[vector_def]

        msg_type_str = "----" + __name__.replace('.','/') + self.nl
        if type_def_str:
            msg_type_str += self.add_tabs(type_def_str, 1) + self.nl
        msg_type_str += self.add_tabs(msg_record_str, 1)

        config.super_type_defs = self.super_type_defs

        murphi_str.append(msg_type_str)
