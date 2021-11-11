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

from DataObjects.States.ClassStatev2 import State_v2
from typing import List


class StateSet:
    def __init__(self, state: State_v2):

        assert isinstance(state, State_v2), str(state) + " is of type:" + str(type(state))

        self.stable_state: State_v2 = state

        self.states: List[State_v2] = [state]
        self.start_states: List[State_v2] = []
        self.end_states: List[State_v2] = [state]

    def __str__(self):
        return str(self.stable_state) + ': ' + ', '.join(str(e) for e in self.states)

########################################################################################################################
# STABLE STATE
########################################################################################################################

    def getstablestate(self) -> State_v2:
        return self.stable_state

    def add_start_state(self, state: State_v2):
        # Stable states aren't added to state sets
        if state.stable:
            return

        if state not in self.states:
            self.states.append(state)
        if state not in self.start_states:
            self.start_states.append(state)
            state.start_state_set.append(self)

    def add_end_state(self, state: State_v2):
        # Stable states aren't added to state sets
        if state.stable:
            return

        if state not in self.states:
            self.states.append(state)
        if state not in self.end_states:
            self.end_states.append(state)
            state.end_state_set.append(self)

    def remove_state(self, state):
        state.remove_state_set(self)
        if state in self.states:
            self.states.remove(state)
        if state in self.start_states:
            self.start_states.remove(state)
        if state in self.end_states:
            self.end_states.remove(state)

    def removestates(self, states):
        for state in states:
            self.remove_state(state)
