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

#
#
#

import copy
from typing import List, Union

from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.States.ClassStatev2 import State_v2

from DataObjects.FlowDataTypes.ClassMessage import Message
from DataObjects.FlowDataTypes.ClassEvent import Event, EventAck
from DataObjects.FlowDataTypes.ClassBaseAccess import Access, Evict
from Parser.DataTypes.ClassGuard import Guard


class Trace:
    def __init__(self, transitions: List[Transition_v2]):
        self.trace_trans: List[Transition_v2] = transitions
        self.states: List[State_v2] = []

        # List the guards
        self.init_guard: [Message, Event, Access, Evict, Guard] = None

        # The total sequence of guards existing
        self.all_guards: [Message, Event, EventAck, Access, Evict, Guard] = []
        # All guards of type message, required for the model checker
        self.guards_msg: List[Union[Message, Guard]] = []
        # All guards of type event and event ack
        self.guards_event: List[Union[Event, EventAck]] = []
        # Guard accesses
        self.guards_access: List[Union[Access, Evict]] = []

        self.out_msg: List[Message] = []
        self.out_events: List[Event] = []

        self.start_state: State_v2 = None
        self.final_state: State_v2 = None

        self.update_messages_and_states()

        self.update_final_states()

    def __str__(self):
        state_str = str(self.start_state)
        for ind in range(0, len(self.trace_trans)):
            state_str += " --" + str(self.trace_trans[ind].guard) + "-- " + str(self.trace_trans[ind].final_state)
        return state_str

    def __hash__(self):
        return hash(tuple((hash(transition) for transition in self.trace_trans)))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __add__(self, other: 'Trace'):
        new_trace = copy.copy(self)
        new_other = copy.copy(other)

        new_trace.trace_trans: List[Transition_v2] = copy.copy(new_other.trace_trans)
        new_trace.states = copy.copy(new_trace.states)
        new_trace.out_msg = copy.copy(new_trace.out_msg)
        new_trace.in_msg = copy.copy(new_trace.in_msg)
        new_trace.access = copy.copy(new_trace.access)

        for state in new_other.states:
            if state not in new_trace.states:
                new_trace.states.append(state)

        new_trace.update_messages_and_states()
        new_trace.update_final_states()

        return new_trace

    def update_messages_and_states(self):
        if not self.trace_trans:
            print("HOLD")

        self.states: List[State_v2] = [trans.start_state for trans in self.trace_trans] + \
                                      [self.trace_trans[-1].final_state]
        self.init_guard = self.trace_trans[0].guard
        for trans in self.trace_trans:
            if isinstance(trans.guard, (Event, EventAck)):
                self.guards_event.append(trans.guard)
            elif isinstance(trans.guard, (Access, Evict)):
                self.guards_access.append(trans.guard)
            else:
                self.guards_msg.append(trans.guard)
            self.all_guards.append(trans.guard)

        self.out_msg = [out_msg for trans in self.trace_trans for out_msg in trans.out_msg if out_msg]
        self.out_events = [trans.out_event for trans in self.trace_trans if trans.out_event]

    def update_final_states(self):
        if self.trace_trans:
            self.start_state = self.trace_trans[0].start_state
            self.final_state = self.trace_trans[-1].final_state
