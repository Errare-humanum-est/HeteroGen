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
from typing import List, Union

from DataObjects.FlowDataTypes.ClassMessage import Message
from DataObjects.FlowDataTypes.ClassEvent import Event, EventAck
from DataObjects.ClassBaseState import SSPState
from DataObjects.Transitions.ClassBaseTransition import BaseTransition

from Parser.DataTypes.ClassGuard import Guard

from DataObjects.FlowDataTypes.ClassBaseAccess import Access, Evict


class Transition_v2(BaseTransition):
    def __init__(self,
                 start_state: Union[SSPState, 'State_v2'],
                 final_state: Union[SSPState, 'State_v2'],
                 operations: List[CommonTree],
                 guard: Union[Message, Event, EventAck, Access, Evict, Guard],
                 out_msg: List[Message] = None,
                 out_event: Event = None):

        BaseTransition.__init__(self, start_state, final_state, operations, guard, out_msg, out_event)

        # Communication class from ClassCommClassFunc
        self.comm_class: str = None
        self.serialized: bool = None

        # Inherits BaseTransition __str__ and __hash__ functions
