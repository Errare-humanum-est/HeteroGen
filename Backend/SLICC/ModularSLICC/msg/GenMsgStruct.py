#  Copyright (c) 2022.  Nicolai Oswald
#  Copyright (c) 2022.  University of Edinburgh
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
#
#

from DataObjects.ClassCluster import Cluster
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from Backend.SLICC.ModularSLICC.common import Util
from Backend.SLICC.ModularSLICC import SLICCTokens


class GenMsgStruct(TemplateHandler):

    template_file = "msg_structure.sm"

    def __init__(self, handler_dir: str):
        TemplateHandler.__init__(self, handler_dir)

    def gen_msg_struct_str(self, cluster: Cluster):
        const_str = "//" + __name__ + self.nl
        variables = {}

        for global_arch in cluster.get_global_architectures():
            for msg_type in global_arch.network.msg_types.values():
                variables.update(msg_type.msg_vars)

        body = ""
        for var, var_type_tree in variables.items():
            method_fct = SLICCTokens.data_type_map[str(var_type_tree)]
            method = getattr(self, method_fct, lambda: '_pass_node')
            body += f"{self.tab}{method(var)}"

        # NOTE/TODO just like GenMachInPorts.py, we need to know which Data object functional reads and writes
        # operate on. Therefore, assuming the message types declare PRECISELY ONE DATA OBJECT
        data_var = Util.get_message_data_var(cluster)

        const_str += self.string_repl_keys(self.open_template(GenMsgStruct.template_file), [body, data_var])
        return const_str

    def _pass_node(self, var: str) -> str:
        return ""

    def _set_init_state(self, var: str) -> str:
        return ""

    def _gen_cache_line(self, var: str) -> str:
        return f"DataBlock {var}, desc=\"Cache line / Data {var}\"{self.end}"

    def _gen_identifier(self, var: str) -> str:
        return f"MachineID {var}, desc=\"Machine identifier {var}\"{self.end}"

    def _gen_int(self, var: str) -> str:
        return f"int {var}, desc=\"Integer {var}\"{self.end}"

    def _gen_bool(self, var: str) -> str:
        raise NotImplementedError

    def _gen_msg(self, var: str) -> str:
        raise NotImplementedError
