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
from typing import List, Union

from antlr3.tree import CommonToken, CommonTree
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase

from DataObjects.FlowDataTypes.ClassMessage import Message, BaseMessage
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.Architecture.ClassBaseArchitecture import BaseArchitecture
from Algorithms.ControllerGeneration.General.DeferMessage.BaseDeferMessage import BaseDeferMessage


class NestedDeferMessage(BaseDeferMessage):
    proxy_key = 'proxy_msg'

    def __init__(self, base_arch: BaseArchitecture):
        BaseDeferMessage.__init__(self)
        self.update_base_arch_global_variable(base_arch)

    def update_base_arch_global_variable(self, base_arch: BaseArchitecture):
        new_operation = CommonTree(CommonToken(text=ProtoParserBase.t_msg))
        # Left side assignment
        new_operation.addChild(CommonTree(CommonToken(text=self.proxy_key)))
        base_arch.machine.variables[self.proxy_key] = new_operation

    def push_defer_guard_proxy_transitions(self, transitions: List[Transition_v2],
                                           cur_guard: Union[BaseMessage, Message],
                                           new_guard: Union[BaseMessage, Message]):
        for transition in transitions:
            if transition.guard == cur_guard:
                transition.guard = new_guard
                transition.operations.append(self.push_defer_message(self.proxy_key, str(new_guard)))

    def pop_defer_guard_proxy_transitions(self, transitions: List[Transition_v2],
                                          cur_guard: Union[BaseMessage, Message],
                                          new_guard: Union[BaseMessage, Message]):
        for transition in transitions:
            if transition.guard == cur_guard:
                transition.guard = new_guard
            transition.rename_operation(str(cur_guard), self.proxy_key)

