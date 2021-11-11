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

from Backend.Murphi.BaseConfig import BaseConfig
from Backend.Common.TemplateHandler.TemplateBase import TemplateBase
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens


class GenAdrDef(TemplateBase):

    def __init__(self, murphi_str: List[str], config: BaseConfig):
        TemplateBase.__init__(self)

        access_str = "----" + __name__.replace('.','/') + self.nl
        if config.litmus_testing:
            access_str += (MurphiTokens.k_address + ": 0.." + MurphiTokens.c_adr_cnt_const + self.end)
        else:
            access_str += (MurphiTokens.k_address + ": " + MurphiTokens.k_scalar_set +
                           "(" + MurphiTokens.c_adr_cnt_const + ")" + self.end)
        access_str += MurphiTokens.k_cl_val + ": 0.." + MurphiTokens.c_val_cnt_const + self.end

        murphi_str.append(access_str + self.nl)
