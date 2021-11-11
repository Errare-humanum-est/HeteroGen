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
#

from typing import Dict, List

from DataObjects.ClassState import State
from Deprecated.ClassTransition import Transition

''' Functions parse input from Parser and generate State objects'''


########################################################################################################################
# 1) INPUT PROCESSING -- CC/DC
########################################################################################################################

# Creates the state objects that contain its corresponding ssp_transitions
def create_states(transitions: List[Transition], access: List[str], evict: List[str]) -> Dict[str, State]:
    states = convert_statenodes_to_states(transitions, access, evict)
    update_transitions(states, transitions)
    return states


# Sorts the states given in all initial ssp_transitions given in parser
def sort_states(transitions: List[Transition]) -> Dict[str, List[Transition]]:
    statetransmap = {}
    startnames = []
    finalnames = []

    for transition in transitions:
        startstate = transition.getstartstate().getstatename()
        finalstate = transition.getfinalstate().getstatename()

        if startstate != finalstate:
            startnames.append(startstate)
            finalnames.append(finalstate)

        if startstate in statetransmap:
            statetransmap.update({startstate: statetransmap[startstate] + [transition]})
        else:
            statetransmap.update({startstate: [transition]})

    return statetransmap


# Convert StateNode objects from Parser to State objects used by Algorithm
def convert_statenodes_to_states(transitions: List[Transition], access: List[str], evict: List[str]) -> Dict[str, State]:
    states = {}
    statetransmap = sort_states(transitions)
    for statename in statetransmap:
        # Create a new state object
        states.update({statename: State(statename, access, evict)})
        states[statename].addtransitions(statetransmap[statename])
    return states


# Replace StateNode objects of parser with new created State objects
# This points each Transition to its start and end State and points the State objects to their Transition as well
def update_transitions(states: Dict[str, State], transitions: List[Transition]):
    for transition in transitions:
        transition.setstartstate(states[transition.getstartstate().getstatename()])
        try:
            transition.setfinalstate(states[transition.getfinalstate().getstatename()])
        except KeyError:
            assert 0, "Unknown final state"
