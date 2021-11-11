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

from typing import Dict, List

from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.ClassTrace import Trace
from DataObjects.FlowDataTypes.ClassEvent import EventAck, Event

from Debug.Monitor.ClassDebug import Debug

from DataObjects.CommClassification.ClassBaseCommClass import BaseCommClass

from DataObjects.Architecture.ClassGlobalBaseArchitecture import GlobalBaseArchitecture, BaseAccess


class CommClassFunc(BaseCommClass, Debug):

    def __init__(self, trans_trace_dict: Dict[State_v2, List[Trace]],
                 base_architecture: GlobalBaseArchitecture):
        Debug.__init__(self, True)
        BaseCommClass.__init__(self)

        for state in trans_trace_dict:
            self.classify_trans_traces(trans_trace_dict[state], base_architecture)

    def classify_trans_traces(self, trans_traces: List[Trace], base_architecture: GlobalBaseArchitecture):
        for trans_trace in trans_traces:
            self.classify_transitions(trans_trace, base_architecture)

    def classify_transitions(self, trace: Trace, base_architecture: GlobalBaseArchitecture):
        self.first_transition(trace.trace_trans[0], len(trace.trace_trans), base_architecture)

        for ind in range(1, len(trace.trace_trans)):
            self.trail_transitions(trace.trace_trans[ind], base_architecture)

    def trail_transitions(self, transition: Transition_v2, base_architecture: GlobalBaseArchitecture):
        if isinstance(transition.guard, EventAck):      # Also add type checking
            if transition.out_msg:
                self.check_and_set_trans_class(transition, self.evnt_req)
            else:
                self.check_and_set_trans_class(transition, self.evnt_resp)
        elif str(transition.guard) in base_architecture.network.base_message_dict:
            if transition.out_msg:
                self.check_and_set_trans_class(transition, self.resp_resp)
            else:
                self.check_and_set_trans_class(transition, self.resp)
        else:
            self.pwarning("Unable to identify communication pattern, transition handled as response")
            self.check_and_set_trans_class(transition, self.resp)
            #self.perror("Unexpected communication behaviour: " + str(transition))

        transition.start_state.add_classify_trans(transition)

    def first_transition(self, transition: Transition_v2, trans_len: int,
                         base_architecture: GlobalBaseArchitecture) -> str:

        # Check if transition is triggered by an access request
        if isinstance(transition.guard, BaseAccess.Access):
            if transition.out_msg:
                self.check_and_set_trans_class(transition, self.acc_req)
            else:
                self.check_and_set_trans_class(transition, self.acc)

        # Check if transition is triggered by an evict request
        elif isinstance(transition.guard, BaseAccess.Evict):
            if transition.out_msg:
                self.check_and_set_trans_class(transition, self.evi_req)
            else:
                self.check_and_set_trans_class(transition, self.evi)

        # Check if transition is triggered by an event
        elif isinstance(transition.guard, Event):
            if transition.out_msg:
                if trans_len > 1:
                    self.check_and_set_trans_class(transition, self.evnt_req)
                else:
                    self.check_and_set_trans_class(transition, self.evnt_resp)
            else:
                self.check_and_set_trans_class(transition, self.evnt)

        # Check if transition is triggered by a remote request
        elif str(transition.guard) in base_architecture.network.base_message_dict:
            if transition.out_msg:
                if trans_len > 1:
                    self.check_and_set_trans_class(transition, self.rem_req)
                else:
                    self.check_and_set_trans_class(transition, self.rem_resp)
            else:
                self.check_and_set_trans_class(transition, self.rem)

        else:
            self.perror("Unexpected communication behaviour: " + str(transition))

        transition.start_state.add_classify_trans(transition)

        return transition.comm_class

    def check_and_set_trans_class(self, transition: Transition_v2, classification: str):
        if not transition.comm_class:
            transition.comm_class = classification
            return

        if transition.comm_class != classification:
            self.pwarning("Communication classification mismatch: " + transition.comm_class + " and " + classification)

        return transition.comm_class
