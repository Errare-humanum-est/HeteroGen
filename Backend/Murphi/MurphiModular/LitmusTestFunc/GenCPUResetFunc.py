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
from Backend.Murphi.BaseConfig import BaseConfig


class GenCPUResetFunc(TemplateHandler):

    def __init__(self, murphi_str: List[str], config: BaseConfig):
        TemplateHandler.__init__(self)

        cpu_reset_str_list: List[str] = []

        self.check_reset_cpus(cpu_reset_str_list)
        self.gen_cpu_instances(cpu_reset_str_list, config)
        self.reset_cpus(cpu_reset_str_list)

        murphi_str.append("------" + __name__.replace('.','/') + self.nl + self.add_tabs(''.join(cpu_reset_str_list), 1))

    def check_reset_cpus(self, cpu_reset_str_list: List[str]):
        cpu_reset_str_list.append(self._openTemplate(MurphiTemplates.f_cpu_check_reset) + self.nl + self.nl)

    def gen_cpu_instances(self, cpu_reset_str_list: List[str], config: BaseConfig):
        cpu_def = "procedure Instr(var f: OBJ_CPU)" + self.end
        cpu_def += "begin" + self.nl

        for ind in range(0, config.c_cpu_count):
            cpu_def += self.tab + "CPU" + str(ind) + "_Instr(f)" + self.end

        cpu_def += "end" + self.end + self.nl

        cpu_reset_str_list.append(cpu_def)

    def reset_cpus(self, cpu_reset_str_list: List[str]):
        cpu_reset_str_list.append(self._openTemplate(MurphiTemplates.f_cpu_reset_func) + self.nl)
