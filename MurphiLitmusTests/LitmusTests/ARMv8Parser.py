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

from os import listdir
from os.path import isfile, join

import re
from typing import List, Dict

from DataObjects.ClassMultiDict import MultiDict
from MurphiLitmusTests.ClassLitmusTest import LitmusTest, LitmusThread
from MurphiLitmusTests.ClassLitmusInstruction import StoreInstruction, LoadInstruction
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess


class ARMv8Parser:

    k_acquire = 'acquire'
    k_release = 'release'

    def __init__(self, file_path: str, mem_consist_model: str = ""):
        self.litmus_test_list: List[LitmusTest] = []
        self.mem_consist_model = mem_consist_model
        self.gen_litmus_tests(file_path)

    def gen_litmus_tests(self, file_path: str):
        file_list = sorted([f for f in listdir(file_path) if (isfile(join(file_path, f)) and f.endswith(".litmus"))])

        for litmus_test in file_list:
            self.gen_litmus_test_obj(litmus_test, open(file_path + "/" + litmus_test).read().replace('\n', ''))

    def gen_litmus_test_obj(self, test_name: str, test_str: str):
        litmus_test = LitmusTest(test_name, self.mem_consist_model)
        # Determine processor variable mapping
        litmus_test.processor_reg_var_map_dict = self.map_variables_to_processors(test_str)
        # Generate the litmus threads
        self.gen_threads(litmus_test, test_str)
        # Add the checking condition here as well
        self.gen_exist_cond(test_str, litmus_test)
        self.litmus_test_list.append(litmus_test)

    @staticmethod
    def map_variables_to_processors(test_str: str) -> Dict[int, Dict[str, str]]:
        map_str = re.findall(r"\{\s*(([\w\:\=\s\;])*)\s*\}", test_str)[0]
        mapping_strs = re.findall(r"(\d+\:\w+\=\w)", map_str[0])
        processor_reg_var_map_dict: Dict[int, Dict[str, str]] = {}

        for mapping_str in mapping_strs:
            processor_number = int(re.findall(r"(\d+)\:", mapping_str)[0])
            if processor_number not in processor_reg_var_map_dict:
                processor_reg_var_map_dict[processor_number] = {}
            map_tuple = re.findall(r"(\w+)\=(\w)", mapping_str)[0]
            processor_reg_var_map_dict[processor_number][map_tuple[0]] = map_tuple[1]

        return processor_reg_var_map_dict

    def gen_threads(self, litmus_test: LitmusTest, litmus_threads: str):
        for instr_thread, instr_thread_list in self.gen_thread_inst_list(litmus_threads).items():
            var_val_map: Dict[str, str] = {}
            thread = LitmusThread(instr_thread)
            for instr in instr_thread_list:
                if 'MOV' in instr:
                    mov_store = re.findall(r"MOV\s+(\w+)\,\#(\d+)", instr)[0]
                    var_val_map[mov_store[0]] = mov_store[1]
                elif 'ST' in instr:
                    store_instr = re.findall(r"(\w+)", instr)
                    instr_type = BaseAccess.k_store
                    if 'STLR' in instr:
                        instr_type = self.k_release
                    thread.add_instruction(StoreInstruction(
                        litmus_test.processor_reg_var_map_dict[instr_thread][store_instr[2]],
                        var_val_map[store_instr[1]], instr_type))
                elif 'LD' in instr:
                    load_instr = re.findall(r"(\w+)", instr)
                    instr_type = BaseAccess.k_load
                    if 'LDAR' in instr:
                        instr_type = self.k_acquire
                    reg_str = 'X' + re.findall(r"(\d+)", instr)[0]  # Register are named W#, while exist uses X#
                    thread.add_instruction(LoadInstruction(
                        litmus_test.processor_reg_var_map_dict[instr_thread][load_instr[2]],
                        reg_str, instr_type))
            litmus_test.add_thread(thread)

    @staticmethod
    def gen_thread_inst_list(litmus_threads: str) ->MultiDict:
        instr_line_sequences = [instr_seq[0] for instr_seq in re.findall(r"([\w\s\d\\#\,\[\]]+(\|[\w\s\d\\#\,\[\]]*)+)",
                                                                         litmus_threads)]
        instr_thread_lists: MultiDict = MultiDict()
        for instr_line_sequence in instr_line_sequences[1:]:
            instr_threads = instr_line_sequence.split("|")
            for instr_thread_ind in range(0, len(instr_threads)):
                instr_thread_lists[instr_thread_ind] = re.findall(r"(\w+\s\w+\,[\#\w\[\]]+)",
                                                                  instr_threads[instr_thread_ind])
        return instr_thread_lists

    @staticmethod
    def gen_exist_cond(instr_str: str, litmus_test: LitmusTest):
        check_exist_true = re.findall(r"\;\s*(\~*)exists", instr_str)[0]
        if check_exist_true:
            litmus_test.exists = False

        for exist_check in re.findall(r"(\d+\:\w\d+\=\d+)", instr_str):
            processor = int(re.findall(r"(\d+)\:", exist_check)[0])
            exist = re.findall(r"\d+\:(\w\d+)\=(\d+)", exist_check)[0]
            litmus_test.threads[processor].reg_val_exist[exist[0]] = int(exist[1])
