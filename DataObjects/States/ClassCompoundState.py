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
from typing import Tuple
from DataObjects.States.ClassStatev2 import State_v2


class CompoundState(State_v2):

    def __init__(self, base_states: Tuple[State_v2, ...], prefix: str = ""):
        state_str = '__C__'.join(str(base_state) for base_state in base_states)
        self.prefix = prefix
        if prefix:
            state_str = str(prefix) + state_str
        State_v2.__init__(self, state_str)
        self.base_states: Tuple = base_states

        self.stable = True
        for state in self.base_states:
            if not state.stable:
                self.stable = False
                break

    def __str__(self):
        return super().__str__()

    def __hash__(self):
        return hash((hash(self.base_states), str(self.prefix)))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def get_compound_states(self) -> Tuple[State_v2, ...]:
        return tuple(state for proxy_dir_state in self.base_states for state in proxy_dir_state.get_compound_states())
