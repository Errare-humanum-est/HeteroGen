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

from typing import List, Dict

from networkx import MultiDiGraph

from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.ClassStateSet import StateSet
from DataObjects.ClassTrace import Trace
from DataObjects.CommClassification.ClassBaseCommClass import BaseCommClass


## StateSetsNetworkx
#
#  State container
#  Dependency: BaseCommClass
class StateSetsNetworkx:

    def __init__(self, trans_trace_dict: Dict[State_v2, List[Trace]]):

        self.state_sets: Dict[State_v2, StateSet] = {}

        # StateSet init
        for stable_state in trans_trace_dict:
            self.state_sets[stable_state] = StateSet(stable_state)
            stable_state.end_state_set.append(self.state_sets[stable_state])

        # Assign the transient states to traces
        for stable_state in trans_trace_dict:
            # State set assignment of the states
            self.end_set_search(trans_trace_dict[stable_state])
            self.start_set_search(trans_trace_dict[stable_state])

    def cache_dir_assignment(self):
        pass

    def cache_snoop_assignment(self):
        pass

    def dir_assignment(self):
        pass

    # All states in a trace are element of the final state set
    def end_set_search(self, trans_traces: List[Trace]):
        for trace in trans_traces:
            end_set = self.state_sets[trace.final_state]

            # If no response is required then final state of first transition is stable state -> continue
            if len(trace.trace_trans) < 2:
                continue

            for ind in range(0, len(trace.trace_trans)):
                if ind < len(trace.trace_trans)-1:
                    end_set.add_end_state(trace.trace_trans[ind].final_state)

    # A directory response message list can be used to identify the serialization messages
    # The serial response messages can be probably extracted from the atomic model checker
    def start_set_search(self, traces: List[Trace]):
        for trace in traces:
            start_set = self.state_sets[trace.start_state]

            # From a remote request the serialization can be inferred,
            # the remote request final state set is entered immediately
            if trace.trace_trans[0].comm_class == BaseCommClass.rem or \
                    trace.trace_trans[0].comm_class == BaseCommClass.rem_resp or \
                    trace.trace_trans[0].comm_class == BaseCommClass.rem_req:
                continue

            # If no response is required then final state of first transition is stable state -> continue
            if len(trace.trace_trans) < 2:
                continue

            # Assuming after the first response message, serialization has happened.
            # This will be improved in the near future by utilizing the model checker
            start_set.add_start_state(trace.trace_trans[0].final_state)

    def get_states_from_state_sets(self) -> List[State_v2]:
        states = []
        for state_set in self.state_sets.values():
            for state in state_set.states:
                states.append(state)

        states = list(set(states))
        states.sort(key=lambda state: str(state))
        return states

    @ staticmethod
    def graph_extract_transitions(fsm_graph: MultiDiGraph) -> List[Transition_v2]:
        return [edge[2]['transition'] for edge in fsm_graph.edges.data()]

