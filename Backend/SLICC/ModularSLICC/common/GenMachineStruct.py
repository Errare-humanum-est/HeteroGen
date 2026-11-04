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
from antlr3.tree import CommonTree
from DataObjects.Architecture.ClassBaseArchitecture import BaseArchitecture
from Parser.ProtoCCcomTreeFct import objListToStringList
from Backend.SLICC.ModularSLICC import SLICCTokens
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler


class GenMachineStruct:

    @staticmethod
    def gen_machine_struct_body_str(temp_h: TemplateHandler, arch: BaseArchitecture) -> str:
        body_strs = []
        for variable in arch.machine.variables.values():
            # TODO this basic version does not track GlobalInit a la Murphi backend...
            # In the future, will probably encounter a scenario where this is needed, upon
            # which time this should be extended.
            # For now, only generating the structure entry itself
            method_fct = SLICCTokens.data_type_map.get(variable.getText(), '_pass_node')
            method = getattr(GenMachineStruct, method_fct)
            res = method(variable)
            if res:
                body_strs.append(temp_h.tab + res)

        return temp_h.nl.join(body_strs)

    ####################################################################################################################
    # DATA TYPE GENERATION
    ####################################################################################################################

    @staticmethod
    def _pass_node(definition: CommonTree) -> bool:
        return False

    @staticmethod
    def _set_init_state(definition: CommonTree) -> bool:
        # The initial state has already been generated in [GenDirStateDecl]
        return False

    @staticmethod
    def _gen_cache_line(definition: CommonTree) -> str:
        tokens = definition.getChildren()
        return f"{SLICCTokens.st_data} {tokens[-1].getText()}, desc=\"... TODO ...\";"

    @staticmethod
    def _gen_identifier(definition: CommonTree) -> str:
        tokens = definition.getChildren()
        if len(tokens) > 1:
            return GenMachineStruct._gen_net_dest(tokens)
        else:

            return f"{SLICCTokens.st_mach_id} {tokens[-1].getText()}, desc=\"... TODO ...\";"

    @staticmethod
    def _gen_net_dest(tokens: List[CommonTree]) -> str:
        # For now, assuming only using sets to refer to other machines
        return f"{SLICCTokens.st_net_dest} {tokens[0].getText()}, desc=\"... TODO ...\";"

    @staticmethod
    def _gen_int(definition: CommonTree) -> str:
        # Unlike Murphi, SLICC is not a verification engine and therefore does not
        # require ints to be bounded
        tokens = definition.getChildren()
        return f"{SLICCTokens.st_int} {tokens[0].getText()}, default={tokens[-1].children[0].getText()}, " \
               "desc=\"...TODO...\";"

    @staticmethod
    def _gen_bool(definition: CommonTree) -> str:
        raise NotImplementedError

    @staticmethod
    def _gen_msg(definition: CommonTree) -> str:
        return "".join(objListToStringList([definition]))
