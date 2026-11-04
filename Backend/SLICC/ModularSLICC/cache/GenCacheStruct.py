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

from DataObjects.Architecture.ClassBaseArchitecture import BaseArchitecture
from Backend.SLICC.ModularSLICC import SLICCTokens
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from Backend.SLICC.ModularSLICC.common import Util
from Backend.SLICC.ModularSLICC.common.GenMachineStruct import GenMachineStruct


class GenCacheStruct(TemplateHandler):
    template_file = "entry_structure.sm"

    """
        TODO SLICC adds complexity in that some of a machine's variables
        should go in the TBE, not the Entry... ignoring this for now and just putting it all in the Entry.
    """

    def __init__(self, handler_dir: str):
        TemplateHandler.__init__(self, handler_dir)

    def gen_cache_struct_str(self, arch: BaseArchitecture) -> str:
        const_str = "//" + __name__ + self.nl
        body = None
        for var_name, variable in arch.machine.variables.items():
            # For caches, put only the stable states and the cache line in the Entry.
            # The other variables should go in the TBE.

            if var_name == Util.get_active_cache_line(arch):
                method_fct = SLICCTokens.data_type_map.get(variable.getText(), '_pass_node')
                method = getattr(GenMachineStruct, method_fct)
                res = method(variable)
                if res:
                    body = self.nl + self.tab + res
                    break
        assert body is not None, "No cache line found"

        const_str += self.string_repl_keys(self.open_template(GenCacheStruct.template_file),
                                           ["", "Cache", body]
                                           )
        return const_str + self.nl
