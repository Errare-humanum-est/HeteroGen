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
from typing import List

from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.ClassTrace import Trace

from Debug.Monitor.ClassDebug import Debug


class Machine:
    def __init__(self, arch: 'FlatArchitecture'):
        self.arch: 'FlatArchitecture' = arch
        self.covered_traces: List[Trace] = []

        self.start_state: State_v2 = self.arch.init_state
        self.final_state: State_v2 = self.arch.init_state
        self.cur_trace: Trace = None

    def __str__(self):
        return str(self.arch)

    def __hash__(self):
        return hash((str(self.arch), str(self.start_state), str(self.final_state), hash(self.cur_trace)))

    def __eq__(self, other):
        return hash(self) == hash(other)

    # This is a legacy function to handle machines that inherit multiple architectures
    def get_arch_list(self):
        return self.arch.get_arch_list()

    def update_trace(self, trace: Trace) -> 'Machine':
        new_machine_state = copy.copy(self)
        new_machine_state.cur_trace = trace
        # Trace can be none
        if trace:
            if not(trace.start_state in self.arch.stable_states and trace.final_state in self.arch.stable_states):
                Debug.perror("Start and final state of trace not object of current architecture")
            new_machine_state.start_state = trace.start_state
            new_machine_state.final_state = trace.final_state
            # Add trace to the covered traces
            if trace not in self.covered_traces:
                self.covered_traces.append(trace)
        else:
            # If no trace is given, the new state's start and final state become the final state of its predecessor
            new_machine_state.start_state = self.final_state
            new_machine_state.final_state = self.final_state
        return new_machine_state

    def add_idle(self) -> 'Machine':
        new_machine_state = copy.copy(self)
        new_machine_state.cur_trace = None
        new_machine_state.start_state = new_machine_state.final_state
        # Add trace to the covered traces
        return new_machine_state

    def get_mach_state_trace_id(self) -> int:
        if self.cur_trace:
            return id(self.cur_trace)
        else:
            ret_val = 0
            if self.start_state:
                ret_val += id(self.start_state)
            if self.final_state:
                ret_val += id(self.final_state)
            return ret_val

    def get_mach_state_trace_str(self) -> str:
        if self.cur_trace:
            return str(self.cur_trace)
        else:
            ret_str = ""
            if self.start_state:
                ret_str += str(self.start_state)
                if self.final_state and self.final_state == self.start_state:
                    return ret_str
                if self.final_state:
                    ret_str += " -> "
            if self.final_state:
                ret_str += str(self.final_state)
            return ret_str
