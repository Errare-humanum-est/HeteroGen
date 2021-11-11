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

from typing import List, Tuple, Union

from DataObjects.FlowDataTypes.ClassBaseAccess import Access, Evict
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.CommClassification.ClassBaseCommClass import CommClassState

from Debug.Monitor.ClassDebug import Debug


## State_v2
#
#  State container
#  Dependency: ClassCommFunc, StateSetsNetworkx
class State_v2(CommClassState, Debug):
    def __init__(self, name: str):
        # Add commclass state property
        CommClassState.__init__(self)

        Debug.__init__(self)

        self.state: str = name
        self.stable: bool = False

        # A list of ssp_transitions starting in this state
        self.state_trans: List[Transition_v2] = []

        self.access_permissions: List[Union[Access, Evict]] = []

        #  Dependency: StateSetsNetworkx
        # First StateSets assignment must be performed
        self.start_state_set = []
        self.end_state_set = []

    def __str__(self):
        return self.state

    # Don't define __hash__ and __eq__ function as state objects won't be found in networkx dict anymore if changed
    # externally. Hence use custom hashing

    def custom_hash(self):
        return hash((str(self.state), (hash(trans) for trans in self.state_trans)))

    ####################################################################################################################
    # STATE TRANSITION
    ####################################################################################################################
    def add_transitions(self, transitions: [Transition_v2, List[Transition_v2]]):
        tmp_trans = transitions
        if not isinstance(transitions, list):
            tmp_trans = [transitions]
        for transition in tmp_trans:
            self.add_transition(transition)

    def add_transition(self, transition: Transition_v2):
        if hash(transition) not in [hash(trans) for trans in self.state_trans]:
            self.pwarning("The transition start state and the assigned state do not match: " + str(transition),
                          transition.start_state != self)
            self.state_trans.append(transition)
            self.add_classify_trans(transition)

    def remove_transitions(self, transitions: [Transition_v2, List[Transition_v2]]):
        if not isinstance(transitions, List):
            transitions = [transitions]

        for transition in transitions:
            if transition in self.state_trans:
                self.state_trans.remove(transition)
                self.remove_classify_trans(transition)

    ####################################################################################################################
    # Compound controller function
    ####################################################################################################################
    def get_compound_states(self) -> Tuple['State_v2']:
        return tuple([self])
