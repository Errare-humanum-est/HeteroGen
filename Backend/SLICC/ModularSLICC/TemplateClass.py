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

import inspect
import os
import re


class TemplateHandler:

    # Constant definitions
    tab = "  "
    nl = "\n"
    sem = ";"
    end = sem + nl

    def __init__(self, template_dir: str):
        self.template_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + \
                            "/../" + template_dir

    ####################################################################################################################
    # REPLACE DYNAMIC
    ####################################################################################################################
    def open_template(self, filename):
        # For gem5 v20 a template of TempSLICC/<dir>_v20 replaces the one of TempSLICC/<dir>
        from Backend.SLICC.ModularSLICC.BackendOptions import OPTIONS, GEM5_V23
        path = self.template_path + "/" + filename
        if OPTIONS.gem5 != GEM5_V23:
            variant = os.path.normpath(self.template_path) + "_" + OPTIONS.gem5 + "/" + filename
            if os.path.exists(variant):
                path = variant
        return re.sub(r'^#.*\n?', '', open(path, "r").read(), flags=re.MULTILINE)

    @staticmethod
    def string_repl_keys(ref_string, replace_keys):
        input_str = ref_string
        for ind in range(0, len(replace_keys)):
            input_str = TemplateHandler._string_repl(input_str, ind, replace_keys[ind])
        return input_str

    @staticmethod
    def _string_repl(string, ind, keyword):
        return re.sub(r"\$" + str(ind) + r"\$", keyword, string)

    def add_tabs(self, string, count):
        tab_string = self.tab * count
        return self.nl.join([tab_string + st for st in string.splitlines()])

    def fix_tabs(self, string: str, base_ident=0):
        current_level = base_ident
        result = []
        for s in string.splitlines():
            s = s.strip()
            if s.startswith("}"):
                current_level -= 1
            result.append((current_level * self.tab) + s)
            if s.endswith("{"):
                current_level += 1

        return self.nl.join(result)

