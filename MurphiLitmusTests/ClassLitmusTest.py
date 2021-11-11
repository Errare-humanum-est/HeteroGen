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

from typing import Set, List, Union, Dict
from MurphiLitmusTests.ClassLitmusThread import LitmusThread


class LitmusTest:

    def __init__(self, test_name: str, memory_consistency_model: str = ""):
        self.test_name: str = test_name
        self.memory_consistency_model: str = memory_consistency_model
        self.threads: Dict[int, LitmusThread] = {}

        self.processor_reg_var_map_dict: Dict[int, Dict[str, str]] = {}

        self.instruction_count: int = 0
        # exists = True, case must be encountered in Litmus test; False it must not be encountered
        self.exists: bool = True
        self.address_count: int = 0
        self.value_max: int = 0
        self.variable_adr_dict: Dict[str, int] = {}

    def add_reg_var_map_dict(self, processor: int, reg_var_dict: Dict[str, str]):
        self.processor_reg_var_map_dict[processor] = reg_var_dict
        self.map_vars_to_address(set(reg_var_dict.values()))

    def add_thread(self, litmus_threads: Union[LitmusThread, List[LitmusThread]]):
        if not hasattr(litmus_threads, '__iter__'):
            litmus_threads = [litmus_threads]

        for litmus_thread in litmus_threads:
            if len(litmus_thread.instructions) > self.instruction_count:
                self.instruction_count = len(litmus_thread.instructions)

            self.map_vars_to_address(litmus_thread.store_var_set)
            self.get_max_value(litmus_thread)
            self.threads[litmus_thread.initial_processor] = litmus_thread

    def map_vars_to_address(self, variables: Set[str]):
        for variable in variables:
            if variable not in self.variable_adr_dict:
                self.variable_adr_dict[variable] = self.address_count
                self.address_count += 1

    def get_max_value(self, litmus_thread: LitmusThread):
        for instruction in litmus_thread.instructions:
            if isinstance(instruction, litmus_thread.store_type):
                if int(instruction.right_assign) > self.value_max:
                    self.value_max = int(instruction.right_assign)

    def __str__(self):
        return self.test_name
