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
from collections import OrderedDict

from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from Backend.SLICC.ModularSLICC.common.GenMachineTransitions import GenMachineTransitions
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture


class GenDirTransitions(TemplateHandler):

    def __init__(self, handler_dir: str):
        TemplateHandler.__init__(self, handler_dir)

    def gen_dir_transitions_str(
            self, arch: FlatArchitecture, main_mem_induced_states: List[str], in_ports: 'OrderedDict[str, str]') -> str:

        all_states = sorted([str(state) for state in arch.get_architecture_states_verified()])
        all_states_str = f"{{{', '.join(all_states)}}}"

        ports = list(in_ports.values())
        ports.append("memQueue_in")
        dealloc_trans_strs = []
        stall_strs = []
        for port in sorted(ports):
            stall_strs.append(
                GenMachineTransitions.gen_stall_transition(self, set(all_states + main_mem_induced_states), port))

        progress_str = GenMachineTransitions.gen_progress_transition(
            self,
            sorted([str(state) for state in arch.get_architecture_states_verified()] + main_mem_induced_states))

        return "//" + __name__ + self.nl \
               + (self.nl * 2).join(dealloc_trans_strs) + (self.nl * 2) \
               + (self.nl * 2).join(stall_strs) + (self.nl * 2) \
               + progress_str + (self.nl * 2) \
               + self.string_repl_keys(self.open_template("transition_alloc_tbe.sm"), [all_states_str]) \
               + (self.nl * 2) \
               + self.string_repl_keys(self.open_template("transition_dealloc_tbe.sm"), [all_states_str]) \
               + self.nl
