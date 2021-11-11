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

from typing import Set, List, Dict, Union
from MurphiLitmusTests.ClassLitmusInstruction import Instruction, LoadInstruction, StoreInstruction, FenceInstruction
Instr_Types = Union[Instruction, LoadInstruction, StoreInstruction, FenceInstruction]


class LitmusThread:

    store_type = StoreInstruction
    load_type = LoadInstruction
    fence_type = FenceInstruction

    def __init__(self, processor_number: int):
        self.initial_processor: int = processor_number
        self.instructions: List[Instr_Types] = []

        # Track the registers and variables
        self.reg_var_map: Dict[str, str] = {}
        self.store_var_set: Set[str] = set()

        # Check the correctness
        self.reg_val_exist: Dict[str, int] = {}

    def __str__(self):
        return "; ".join(str(instr) for instr in self.instructions)

    def add_instruction(self, instruction: Instr_Types):
        self.instructions.append(instruction)

        if isinstance(instruction, self.load_type):
            self.reg_var_map[instruction.left_assign] = instruction.right_assign
        if isinstance(instruction, self.store_type):
            self.store_var_set.add(instruction.left_assign)

    def new_prefetch_instructions_thread(self, instruction_list: List[Instr_Types]):
        new_litmus_thread = LitmusThread(self.initial_processor)
        if hasattr(instruction_list, '__iter__'):
            new_litmus_thread.instructions = list(instruction_list) + self.instructions
        else:
            new_litmus_thread.instructions = self.instructions
        new_litmus_thread.reg_var_map = self.reg_var_map
        new_litmus_thread.store_var_set = self.store_var_set
        new_litmus_thread.reg_val_exist = self.reg_val_exist
        return new_litmus_thread
