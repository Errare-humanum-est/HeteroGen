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

from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess


class Instruction:

    def __init__(self, instr_type: str, left: str, right: str):
        self.instr_type: str = instr_type
        self.left_assign: str = left
        self.right_assign: str = right

    def __str__(self):
        return str(self.instr_type) + " " + str(self.left_assign) + ", " + str(self.right_assign)


class LoadInstruction(Instruction):
    def __init__(self, left_var: str, right_var: str, load_type: str = BaseAccess.k_load):
        Instruction.__init__(self, load_type, left_var, right_var)


class StoreInstruction(Instruction):
    def __init__(self, left_var: str, right_var: str, store_type: str = BaseAccess.k_store):
        Instruction.__init__(self, store_type, left_var, right_var)


class FenceInstruction(Instruction):
    def __init__(self, barrier: str):
        Instruction.__init__(self, barrier, "", "")




