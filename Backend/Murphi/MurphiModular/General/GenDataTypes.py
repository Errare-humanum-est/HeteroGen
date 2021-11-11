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

from antlr3.tree import CommonTree
from typing import Union, Dict

from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Common.TemplateHandler.TemplateBase import TemplateBase

from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from Backend.Murphi.MurphiModular.General.GenPCCToMurphi import GenPCCToMurphi



class GenDataTypes:

    def __init__(self, architecture: str):

        self.architecture: str = architecture

        # Vector definitions
        self.vector_defs: Dict[str, str] = {}

    ####################################################################################################################
    # DATA TYPES
    ####################################################################################################################

    ## Documentation for a method.
    #  @param self The object pointer.
    #  Return object string, initial value
    def gen_data_type(self, data_object: CommonTree, var_name: str = ""):
        method_fct = ProtoParserBase.f_objects[str(data_object)]
        method = getattr(self, method_fct, lambda: '_PassNode')
        return method(data_object, var_name)

    ## Generate an integer
    # Integers always need a range definition
    def _int_func(self, data_object: CommonTree, var_name: str = "") -> str:
        children = data_object.getChildren()
        range_str = ""
        rangedef = children[1].getChildren()
        for ind in range(1, len(rangedef) - 1):
            range_str += rangedef[ind].getText()

        return GenPCCToMurphi.gen_int(int_range=range_str)

    ## Generate a boolean
    def _bool_func(self, data_object: CommonTree, var_name: str = "") -> str:
        return GenPCCToMurphi.gen_bool()

    def _data_func(self, data_object: CommonTree, var_name: str = "") -> str:
        return GenPCCToMurphi.gen_data()

    def _id_func(self, id_obj: CommonTree, var_name: str = "") -> str:
        set_obj_decl = self._find_token_key(id_obj, ProtoParserBase.t_set_val)

        if set_obj_decl:
            # Generate new multiset data type
            return self._gen_multiset(set_obj_decl, var_name)
        else:
            return GenPCCToMurphi.gen_id()

    def _gen_multiset(self, set_obj: CommonTree, var_name: str = "") -> str:
        # The vector name is later extended by
        vector_type = GenPCCToMurphi.gen_vector(var_name)

        # The vector type has been declared before, return
        if vector_type in self.vector_defs:
            return vector_type

        self.vector_defs[var_name] = GenPCCToMurphi.gen_multiset(vector_type, set_obj.getChildren()[0].getText())

        return vector_type

    def _msg_func(self, set_obj: CommonTree, var_name: str = "") -> str:
        return GenPCCToMurphi.gen_message_obj()

    def _PassNode(self, dummy_obj: CommonTree, var_name: str = "") -> str:
        return ""

    @staticmethod
    def _find_token_key(obj_def: CommonTree, key: str) -> Union[CommonTree, None]:
        for child in obj_def.getChildren():
            if str(child) == key:
                return child
        return None
