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

from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Murphi.BaseConfig import BaseConfig
from Debug.Monitor.ClassDebug import Debug


class GenVectorFunc(TemplateHandler, Debug):

    def __init__(self, murphi_str: List[str], config: BaseConfig):
        TemplateHandler.__init__(self)
        Debug.__init__(self)

        vector_func_str = ""

        if config.var_vector_map:
            for vector in config.var_vector_map:
                vector_func_str += (self._stringReplKeys(self._openTemplate(MurphiTemplates.f_vector_func),
                                                         [vector,
                                                          MurphiTokens.k_vector + vector,
                                                          MurphiTokens.k_machines,
                                                          MurphiTokens.k_vector_cnt]) +
                                    self.nl + self.nl)
            murphi_str.append("----" + __name__.replace('.','/') + self.nl + self.add_tabs(vector_func_str, 1))

