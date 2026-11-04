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

from typing import List
from DataObjects.Architecture.ClassBaseArchitecture import BaseArchitecture
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from Backend.SLICC.ModularSLICC.common.GenMachineStateDecl import GenMachineStateDecl


class GenDirStateDecl(TemplateHandler):
    template_file = "state_declaration.sm"

    def __init__(self, handler_dir: str):
        TemplateHandler.__init__(self, handler_dir)

    def gen_dir_state_decl_str(self, arch: BaseArchitecture, main_mem_induced_states: List[str]) -> str:
        const_str = "//" + __name__ + self.nl
        state_declaration_body = GenMachineStateDecl.gen_machine_state_decl_body_str(self, arch) \
                                 + self.nl \
                                 + ''.join([self.string_repl_keys(self.open_template("state_declaration_entry.sm"),
                                                                    [state_name, "Busy"]
                                                                    )
                                            + self.nl
                                            for state_name in main_mem_induced_states
                                            ]
                                           )
        init_state = str(arch.init_state)
        const_str += self.string_repl_keys(self.open_template(GenDirStateDecl.template_file),
                                           ["Directory", init_state, self.add_tabs(state_declaration_body, 1)]
                                           )
        return const_str + self.nl
