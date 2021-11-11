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

from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.ClassTrace import Trace

from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens


class AtomicEvent:

    f_atomic_event_func_template = "Event/AtomicEventFunc.m"
    f_atomic_event_ruleset_template = "RuleSet/AtomicEventRule.m"

    atomic_event_lock_var = "event_lock_adr"

    test_atomic_event_func = "TestAtomicEvent_"
    lock_atomic_event_func = "LockAtomicEvent_"
    unlock_atomic_event_func = "UnlockAtomicEvent_"

    def gen_test_atomic_event_func(self, arch: FlatArchitecture):
        return self.test_atomic_event_func + str(arch) + "(" + MurphiTokens.v_mach + ")"

    def gen_lock_atomic_event_func(self, arch: FlatArchitecture):
        return self.lock_atomic_event_func + str(arch) + "(" + MurphiTokens.v_mach + ", " + MurphiTokens.v_adr + ");"

    def gen_unlock_atomic_event_func(self, arch: FlatArchitecture):
        return self.unlock_atomic_event_func + str(arch) + "(" + MurphiTokens.v_mach + ", " + MurphiTokens.v_adr + ");"

    def check_atomic_event(self, arch: FlatArchitecture,
                           transitions: Union[Transition_v2, List[Transition_v2]]) -> bool:
        if not hasattr(transitions, '__iter__'):
            transitions = [transitions]
        for transition in transitions:
            if self._check_atomic_event(arch, transition):
                return True
        return False

    @staticmethod
    def _check_atomic_event(arch: FlatArchitecture, transition: Transition_v2) -> bool:

        # Looping transitions should not cause events
        if transition.start_state not in arch.stable_states:
            return False

        # Handle looping transitions that do not appear in traces
        if transition.start_state == transition.final_state and not transition.out_event:
            return False

        for sub_tree_list in arch.state_sub_tree_dict[transition.start_state]:
            for trace in arch.get_trans_traces(sub_tree_list, transition.start_state, arch.stable_states):
                trace = Trace(trace)
                if trace.trace_trans[0] == transition and trace.out_events:
                    return True
        return False
