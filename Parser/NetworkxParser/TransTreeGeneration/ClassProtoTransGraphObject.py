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

from antlr3.tree import CommonTree
from typing import Union, List
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase


class ProtoTransGraphObject:

    def __init__(self,
                 object_sequence: Union[None, List[CommonTree]],
                 next_guard: Union[None, CommonTree] = None,
                 final_state_str: str = None):
        self.object_sequence: List[CommonTree] = []
        self.start_guard: Union[None, CommonTree] = None
        self.next_guard: Union[None, List[CommonTree]] = None

        if next_guard:
            self.next_guard = [next_guard]
        # Record start node
        if object_sequence:
            self.object_sequence = object_sequence
            self.start_guard: CommonTree = object_sequence[0]

        # Each TransGraph Object can have only a single final state
        self.final_state_str: str = final_state_str

    # The hash function depends on the object sequence and the final_state that is eventually assigned
    def __hash__(self):
        return hash((tuple(self.object_sequence), self.final_state_str))

    def __str__(self):
        labels = []
        for pcc_object in self.object_sequence:
            if str(pcc_object) == ProtoParserBase.k_guard:
                labels.append(str(pcc_object) + "_" + str(pcc_object.getChildren()[0]))
            else:
                labels.append(str(pcc_object))

        final_state_str = ""
        if self.final_state_str and self.final_state_str != ProtoParserBase.k_state:
            final_state_str = " [" + self.final_state_str + "] "

        return ", ".join(labels) + final_state_str

    def update_next_guard(self, next_guard: List[CommonTree]):
        if not next_guard:
            return

        if self.next_guard:
            if next_guard not in self.next_guard:
                self.next_guard.append(next_guard)
        else:
            self.next_guard = [next_guard]
