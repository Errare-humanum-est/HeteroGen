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
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler

from Debug.Monitor.ClassDebug import Debug


class GenLitmusConst(TemplateHandler, Debug):

    def __init__(self, murphi_str: List[str], config: BaseConfig):
        Debug.__init__(self)

        if config.litmus_testing:
            murphi_str.append(self.cpu_const_str(config))

    def cpu_const_str(self, config: BaseConfig):
        const_str = "---- " + __name__.replace('.','/') + self.nl
        const_str += self.tab + MurphiTokens.c_cpu_cnt + ": " + str(config.c_cpu_count) + self.end
        const_str += self.tab + MurphiTokens.c_instr_cnt + ": " + str(config.c_instr_count) + self.end
        return const_str + self.nl


