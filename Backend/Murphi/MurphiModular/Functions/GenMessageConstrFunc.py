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

from typing import List, Tuple

from DataObjects.ClassCluster import Cluster
from Parser.DataTypes.ClassBaseNetwork import MsgType

from Backend.Murphi.MurphiModular.General.GenDataTypes import GenDataTypes
from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Murphi.BaseConfig import BaseConfig
from Debug.Monitor.ClassDebug import Debug


class GenMessageConstrFunc(GenDataTypes, TemplateHandler, Debug):

    local_msg_var = MurphiTokens.k_message

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        GenDataTypes.__init__(self, self.local_msg_var)
        TemplateHandler.__init__(self)
        Debug.__init__(self)

        msg_constr_func_str_list: List[str] = []

        base_msg_call_str, base_msg_constr_str = self.gen_base_message_constr(config)

        for cluster in clusters:
            for global_arch in cluster.get_global_architectures():
                for msg_type in global_arch.network.msg_types:
                    custom_msg_call_str, custom_msg_constr_str = \
                        self.gen_custom_message_constr(global_arch.network.msg_types[msg_type], config)

                    msg_constr_func_str_list.append(self.gen_message_constr_func(msg_type,
                                                                                 base_msg_call_str,
                                                                                 custom_msg_call_str,
                                                                                 base_msg_constr_str,
                                                                                 custom_msg_constr_str))
        murphi_str.append("----" + __name__.replace('.','/') + self.nl + self.add_tabs(
            "".join(msg_constr_func_str_list), 1) + self.nl)

    def gen_base_message_constr(self, config: BaseConfig) -> Tuple[str, str]:
        base_msg_call_str_list = []
        base_msg_constr_str_list = []
        for def_pair in MurphiTokens.base_msg:
            base_msg_call_str_list.append(self.gen_func_call_assignment(def_pair[0], def_pair[1]))
            base_msg_constr_str_list.append(self.gen_var_assignment(def_pair[0]))
        base_msg_call_str = "; ".join(base_msg_call_str_list)
        base_msg_constr_str = "".join(base_msg_constr_str_list)

        return base_msg_call_str, base_msg_constr_str

    def gen_custom_message_constr(self, msg_type: MsgType, config: BaseConfig) -> Tuple[str, str]:
        custom_msg_call_str_list = []
        custom_msg_constr_str_list = []
        for var_decl in msg_type.msg_vars:
            self.perror("Variable declaration not in super message", var_decl in config.super_type_defs)
            custom_msg_call_str_list.append(
                self.gen_func_call_assignment(var_decl,
                                              self.gen_data_type(config.super_type_defs[var_decl], var_decl)))
            custom_msg_constr_str_list.append(self.gen_var_assignment(var_decl))
        custom_msg_call_str = "; ".join(custom_msg_call_str_list)
        custom_msg_constr_str = "".join(custom_msg_constr_str_list)
        return custom_msg_call_str, custom_msg_constr_str

    @staticmethod
    def gen_func_call_assignment(var_name: str, var_type: str):
        return var_name + ": " + var_type

    def gen_var_assignment(self, var_name: str):
        return self.local_msg_var + "." + var_name + " := " + var_name + self.end

    def gen_message_constr_func(self, msg_type: str, base_msg_call_str: str, custom_msg_call_str: str,
                                base_msg_constr_str: str, custom_msg_constr_str: str):
        func_const_str = MurphiTokens.k_function + " " + msg_type + "(" + base_msg_call_str
        if custom_msg_call_str:
            func_const_str += "; " + custom_msg_call_str
        func_const_str += ") : " + MurphiTokens.k_message + self.end
        func_const_str += MurphiTokens.k_var + " " + self.local_msg_var + ": " + MurphiTokens.k_message + self.end
        func_const_str += MurphiTokens.k_begin + self.nl
        func_const_str += self.add_tabs(base_msg_constr_str + custom_msg_constr_str, 1)
        func_const_str += MurphiTokens.k_return + " " + self.local_msg_var + self.end
        func_const_str += MurphiTokens.k_end + self.end + self.nl

        return func_const_str
