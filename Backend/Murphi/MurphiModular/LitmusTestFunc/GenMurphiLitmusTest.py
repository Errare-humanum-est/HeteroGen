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
#  Copyright (c) 2021.  Nicolai Oswald
#  Copyright (c) 2021.  University of Edinburgh
#  All rights reserved.
#

from typing import List, Union

from MurphiLitmusTests.ClassLitmusTest import LitmusThread
from MurphiLitmusTests.ClassLitmusInstruction import StoreInstruction, LoadInstruction, FenceInstruction
from MurphiLitmusTests.ClassThreadMapLitmusTest import MachThreadMapLitmusTest
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase

from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates


from Debug.Monitor.ClassDebug import Debug

Instructions = Union[StoreInstruction, LoadInstruction, FenceInstruction]


class GenMurphiLitmusTestGen(TemplateHandler, Debug):

    k_none = "none"

    def __init__(self):
        TemplateHandler.__init__(self)
        Debug.__init__(self)

    def gen_murphi_litmus_test(self, litmus_test: MachThreadMapLitmusTest) -> str:
        litmus_test_str = "---- " + litmus_test.test_name + self.nl
        litmus_test_str += self.gen_thread_instr_seq(litmus_test)
        litmus_test_str += self.gen_forbidden_check(litmus_test)
        litmus_test_str += self.gen_cpu_cache_map(litmus_test)
        return litmus_test_str

    def gen_thread_instr_seq(self, litmus_test: MachThreadMapLitmusTest):
        thread_var_body_str = self.gen_thread_instr_var(litmus_test)
        thread_instr_list: List[str] = []
        for processor, thread in litmus_test.threads.items():
            thread_instr_str: str = ""
            for ind in range(0, litmus_test.instruction_count):
                if ind < len(thread.instructions):
                    thread_instr_str += self.gen_thread_instruction(ind, litmus_test, thread.instructions[ind])
                else:
                    thread_instr_str += self.gen_empty_instruction(ind)
            thread_instr_list.append(self.gen_thread_function(processor, thread_var_body_str, thread_instr_str))

        return ''.join(thread_instr_list)

    def gen_thread_instr_var(self, litmus_test: MachThreadMapLitmusTest) -> str:
        instr_var_str = ""
        for ind in range(0, litmus_test.instruction_count):
            instr_var_str += self._stringReplKeys(self._openTemplate(MurphiTemplates.f_instr_seq_var_body),
                                                  [str(ind)])
        return instr_var_str

    def gen_thread_function(self, processor: int, thread_var_body_str: str, thread_var_str: str) -> str:
        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_instr_seq_frame),
                                    [str(processor), thread_var_body_str, thread_var_str]) + self.nl + self.nl

    def gen_thread_instruction(self, instr_number: int,
                               litmus_test: MachThreadMapLitmusTest, instr: Instructions) -> str:
        if isinstance(instr, StoreInstruction):
            return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_instr_seq_body),
                                        [str(instr_number),
                                         instr.instr_type,
                                         str(litmus_test.variable_adr_dict[instr.left_assign]),
                                         str(instr.right_assign)]) + self.nl + self.nl

        if isinstance(instr, (LoadInstruction, FenceInstruction)):
            return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_instr_seq_body),
                                        [str(instr_number),
                                         instr.instr_type,
                                         str(litmus_test.variable_adr_dict[instr.left_assign]),
                                         ProtoParserBase.k_undefined]) + self.nl + self.nl

        Debug.perror("Unrecognized operation type: " + str(type(instr)))

    def gen_empty_instruction(self, instr_number: int) -> str:
        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_instr_seq_body),
                                    [str(instr_number),
                                     ProtoParserBase.k_undefined,
                                     ProtoParserBase.k_undefined,
                                     ProtoParserBase.k_undefined]) + self.nl + self.nl

    def gen_forbidden_check(self, litmus_test: MachThreadMapLitmusTest) -> str:
        cond_check_str: str = ""
        check_count = 0
        for processor, thread in litmus_test.threads.items():
            for reg in sorted(thread.reg_val_exist.keys()):
                instr_ind = self.get_instruction_cond_index(thread, reg)
                cond_check_str += self.gen_cond_check(processor, instr_ind, thread.reg_val_exist[reg])
                check_count += 1

        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_instr_cond_frame),
                                    [cond_check_str, str(check_count)]) + self.nl

    @staticmethod
    def get_instruction_cond_index(thread: LitmusThread, reg_check: str) -> int:
        # Determine instruction position
        for ind in range(len(thread.instructions)-1, -1, -1):
            if isinstance(thread.instructions[ind], LoadInstruction):
                if thread.instructions[ind].right_assign == reg_check:
                    return ind

    def gen_cond_check(self, processor: int, instr_nr: int, value: int) -> str:
        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_instr_cond_body),
                                    [str(processor), str(instr_nr), str(value)]) + self.nl + self.nl

    def gen_cpu_cache_map(self, litmus_test: MachThreadMapLitmusTest) -> str:
        # Generate object sets
        litmus_string = self._openTemplate(MurphiTemplates.f_cpu_cache_map_init) + self.nl

        sorted_archs = set(mach.arch for mach in litmus_test.sorted_mach)
        cache_archs = sorted(sorted_archs, key=lambda x: str(x))

        for cache_type in cache_archs:
            litmus_string += self.add_tabs(
                self._stringReplKeys(self._openTemplate(MurphiTemplates.f_cpu_cache_map_body),
                                     [str(cache_type)]) + self.nl, 1)

        litmus_string += "end" + self.end + self.nl

        return litmus_string
