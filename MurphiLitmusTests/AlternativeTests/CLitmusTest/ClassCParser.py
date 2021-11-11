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
import os
from os import listdir
from os.path import isfile, join

import re
from typing import List, Dict

from MurphiLitmusTests.ClassLitmusTest import LitmusTest, LitmusThread
from MurphiLitmusTests.ClassLitmusInstruction import StoreInstruction, LoadInstruction, FenceInstruction


class CParser:

    def __init__(self):
        self.litmus_test_list: List[LitmusTest] = []
        self.gen_litmus_tests()

    def gen_litmus_tests(self):
        file_path = os.getcwd() + "/RC"
        file_list = [f for f in listdir(file_path) if (isfile(join(file_path, f)) and f.endswith(".litmus"))]

        for litmus_test in file_list:
            self.gen_litmus_test_obj(litmus_test, open(file_path + "/" + litmus_test).read().replace('\n', ''))

    def gen_litmus_test_obj(self, test_name: str, test_str: str):
        litmus_test = LitmusTest(test_name)
        litmus_test.add_thread(self.gen_threads(test_str))
        # Add the checking condition here as well
        self.gen_exist_cond(test_str, litmus_test.threads)
        self.litmus_test_list.append(litmus_test)

    def gen_threads(self, test_str: str):
        thread_dict: Dict[int, LitmusThread] = {}
        litmus_threads = re.findall("(P\d+[^}]*\})", test_str)
        for thread_str in litmus_threads:
            processor_number = int(re.findall(r"P(\d)+", thread_str)[0])
            litmus_thread = LitmusThread(processor_number)
            instr_str = re.findall(r"\{([^}]*)\}", thread_str)[0]
            self.convert_instr_str(instr_str, litmus_thread)
            thread_dict[processor_number] = litmus_thread
        return [thread_dict[ind] for ind in sorted(thread_dict.keys())]

    def convert_instr_str(self, instr_str: str, litmus_thread: LitmusThread):
        instructions = re.findall(r"([^;]+)[^\s]", instr_str)
        # Updated_instr
        for ind in range(0, len(instructions)):
            self.get_load(instructions[ind], litmus_thread)
            self.get_store(instructions[ind], litmus_thread)
            self.get_barrier(instructions[ind], litmus_thread)

    # Convert C operations into load and store operations
    @staticmethod
    def get_load(instr: str, litmus_thread: LitmusThread):
        reg_var_map = re.findall(r"int\s*([^=]+)=\s*\**([^;])*", instr)
        if not reg_var_map:
            return
        reg_var_map = reg_var_map[0]
        litmus_thread.instructions.append(LoadInstruction(reg_var_map[0], reg_var_map[1]))

    @staticmethod
    def get_store(instr: str, litmus_thread: LitmusThread):
        var_val_map = re.findall(r"\*(\w)*.*(\d)+", instr)
        if not var_val_map:
            return
        var_val_map = var_val_map[0]
        litmus_thread.instructions.append(StoreInstruction(var_val_map[0], var_val_map[1]))

    @staticmethod
    def get_barrier(instr: str, litmus_thread: LitmusThread):
        barrier = re.findall(r"atomic_thread_fence\((\w*)\)", instr)
        if not barrier:
            return
        litmus_thread.instructions.append(FenceInstruction(barrier[0]))

    @staticmethod
    def gen_exist_cond(instr_str: str, litmus_threads: List[LitmusThread]):
        litmus_thread_dict: Dict[int, LitmusThread] = {thread.processor: thread for thread in litmus_threads}
        exist_checks = re.findall(r"(\d+\:\w\d+\=\d+)", instr_str)
        for exist_check in exist_checks:
            processor = int(re.findall(r"(\d+)\:", exist_check)[0])
            exist = re.findall(r"\d+\:(\w\d+)\=(\d+)", instr_str)[0]
            litmus_thread_dict[processor].reg_val_exist[exist[0]] = int(exist[1])




parser = CParser()


