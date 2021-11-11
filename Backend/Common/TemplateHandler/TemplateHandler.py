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
#
#

import inspect
import os
import re
from typing import List

from Backend.Common.TemplateHandler.TemplateBase import TemplateBase
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates


class TemplateHandler(TemplateBase):

    def __init__(self):
        TemplateBase.__init__(self)

        self.template_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + \
                             "/../../Murphi/MurphiTemp/" + MurphiTemplates.f_template_dir

    ####################################################################################################################
    # REPLACE DYNAMIC
    ####################################################################################################################
    def _openTemplate(self, filename: str, complete_path: bool = False):
        path = self.template_path + "/" + filename
        if complete_path:
            path = filename
        return re.sub(r'^\#.*\n?', '', open(path, "r").read(), flags=re.MULTILINE)

    def _stringReplKeys(self, ref_string: str, replace_keys: List[str]) -> str:
        input_str = ref_string
        for ind in range(0, len(replace_keys)):
            input_str = self._stringRepl(input_str, ind, replace_keys[ind])
        return input_str

    def _stringRepl(self, string, ind, keyword):
        return re.sub(r"\$" + str(ind) + "\$", keyword, string)

    @staticmethod
    def _testInt(string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    @staticmethod
    def _testOperator(string):
        if string.isalpha():
            return True
        return False
