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
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2


## Creates a transition that chains up two transition traces by merging the last transition of the first trace, with
#  the first transition of the second trace. The second trace initial guard must be an access
#  Used by ProxyDir
#

class ChainTransitions:
    def __init__(self):
        pass

    # If transitions are chained up, the guard of the second transition is removed and all operations are merged into
    # the first transition
    @staticmethod
    def chain_transitions(start_transition: Transition_v2, final_transition: Transition_v2):
        # Unregister the final transition from its assigned start state.
        final_transition.start_state.remove_transitions(final_transition)

        start_transition = start_transition.deepcopy_trans()

        # Remove the final transitions guard operation
        if len(final_transition.operations) > 1:
            start_transition.operations += final_transition.operations[1:]

        # If the guard of the second

        start_transition.out_msg += final_transition.out_msg
        start_transition.final_state = final_transition.final_state

        return start_transition



