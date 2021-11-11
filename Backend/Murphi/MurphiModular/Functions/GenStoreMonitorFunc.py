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

from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates
from Backend.Murphi.BaseConfig import BaseConfig

from Debug.Monitor.ClassDebug import Debug


class GenStoreFunc(TemplateHandler, Debug):

    f_exe_store = "Execute_store_monitor"

    def __init__(self, murphi_str: List[str], config: BaseConfig):
        TemplateHandler.__init__(self)
        Debug.__init__(self)

        access_type_list = []

        if config.enable_read_write_execution and not config.litmus_testing:
            exe_store = self.f_exe_store + "(" + MurphiTokens.v_cbe + ", " + MurphiTokens.v_adr + ");"
            access_type_list.append(self.add_tabs(self._stringReplKeys(self._openTemplate(
                MurphiTemplates.f_store_monitor_func),
                                                                       [MurphiTokens.k_address,
                                                                        MurphiTokens.k_cl_val,
                                                                        MurphiTokens.c_val_cnt_const]),
                1) + self.nl)

            access_type_list.append(self.add_tabs(self._stringReplKeys(self._openTemplate(MurphiTemplates.f_store_func),
                                                                       [MurphiTokens.v_cbe,
                                                                        MurphiTokens.k_cl_val,
                                                                        MurphiTokens.v_adr,
                                                                        MurphiTokens.k_address,
                                                                        MurphiTokens.c_val_cnt_const,
                                                                        exe_store]), 1) + self.nl)
        if access_type_list:
            murphi_str.append("----" + __name__.replace('.','/') + self.nl + "".join(access_type_list))
