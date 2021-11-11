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

from typing import List
from DataObjects.ClassState import State


########################################################################################################################
# 8) STATE MERGING
########################################################################################################################

class MergeStates:

    def __init__(self, max_merging_iterations: int, access: List[str], evict: List[str]):
        self.maxMergingIter = max_merging_iterations
        self.access = access
        self.evict = evict

    def merge_states(self, statesets):
        found = 1
        itercnt = 0

        while found and itercnt < self.maxMergingIter:
            itercnt += 1
            found = 0

            for stateset in statesets:
                defercluster = self._ClusterStatesDeferred(statesets[stateset].getstates())

                for deferkey in sorted(defercluster.keys()):
                    contextcluster = self._ClusterTransitionContext(defercluster[deferkey])

                    for contextkey in sorted(contextcluster.keys()):
                        accesscluster = self._ClusterAccessMerge(contextcluster[contextkey])

                        for accesskey in sorted(accesscluster.keys()):
                            dependencemap = self._ClusterIndependent(accesscluster[accesskey])

                            if len(dependencemap) > 1:
                                transitionmap = self._ClusterTransitions(dependencemap)
                                if (len(transition) > 1 for transition in transitionmap.values()) \
                                        and len(transitionmap):
                                    # To test if states that shall be merged still exist is important
                                    # Greedy algorithm, a state might be mergeable with multiple different states
                                    # After it was merged one, it dissappears and is dead afterwards, therefore any
                                    # possible remaining merging must be deleted
                                    if self._TestStateExistInSet(dependencemap, statesets[stateset]):
                                        self._MergeGivenStates(dependencemap, transitionmap, statesets)
                                        found = 1

    def _GetSetSeq(self, statesets):
        statesetlist = []
        for stateset in statesets.values():
            statesetlist.append(stateset.getstablestate())

        statesetlist.sort(key=lambda x: (len(x.getaccesshit()), x.getstatename()))

        return [state.getstatename() for state in statesetlist]

    def _MergeGivenStates(self, mergestates, transitionmap, statesets):
        mergestates.sort(key=lambda x: len(x.getstatename()))
        # mergestates.sort(key=lambda x: len(x.getstatename()))

        # Make new state
        newstate = State(mergestates[0].getstatename(), self.access, self.evict)

        for transition in transitionmap.values():
            newstate.addtransitions(transition[0])

        # Explore context
        startstatesets = []
        endstatesets = []

        for state in mergestates:
            startstatesets += state.getstartstatesets()
            endstatesets += state.getendstatesets()

        startstatesets = list(set(startstatesets))
        endstatesets = list(set(endstatesets))

        # Remove old states from all state sets
        for stateset in statesets.values():
            stateset.removestates(mergestates)

        # Now add new state to sets
        for stateset in startstatesets:
            stateset.add_start_state(newstate)

        for stateset in endstatesets:
            stateset.add_end_state(newstate)

        # Update links
        for stateset in statesets.values():
            for state in stateset.getstates():
                for replacestate in mergestates:
                    state.replaceremotestate(replacestate, newstate)

    @staticmethod
    def _TestStateExistInSet(states, stateset):
        for state in states:
            if not stateset.teststateexist(state):
                return 0
        return 1

    ####################################################################################################################
    # CLUSTER STATES
    ####################################################################################################################

    def _ClusterStatesDeferred(self, states):
        ordereddeferred = 1

        msgmap = {}

        for state in states:
            defermsgs = state.getdefermessages()

            detectset = []
            for defermsg in defermsgs:
                detectset.append(defermsg.getmsgtype())

            detectkey = '$' + ''.join(detectset if ordereddeferred else detectset.sort())

            entry = msgmap.get(detectkey, 0)
            if entry:
                if state not in entry:
                    entry.append(state)
            else:
                msgmap.update({detectkey: [state]})

        return self._RemoveSingleEntries(msgmap)

    def _ClusterTransitionContext(self, defercluster):
        msgcontextmap = {}

        for state in defercluster:
            for transition in state.getdataack():
                cond = transition.getcond()[0] if transition.getcond() else "_"
                inmsg = transition.getinmsg() if isinstance(transition.getinmsg(), str) else \
                    transition.getinmsg().getmsgtype()

                identkey = inmsg + cond + transition.getfinalstate().getstatename()

                entry = msgcontextmap.get(identkey, 0)
                if entry:
                    entry.append(state)
                else:
                    msgcontextmap.update({identkey: [state]})

        return self._RemoveSingleEntries(msgcontextmap)

    def _ClusterAccessMerge(self, contextcluster):
        accessmap = {}
        for state in contextcluster:
            accesskey = "$"
            for access in state.getaccesshit():
                accesskey += access.getguard()

            entry = accessmap.get(accesskey, 0)
            if entry:
                entry.append(state)
            else:
                accessmap.update({accesskey: [state]})

        return self._RemoveSingleEntries(accessmap)

    def _ClusterIndependent(self, accesscluster):
        dependencemap = {}

        for state in accesscluster:
            for transition in state.gettransitions():
                dependencemap.update({state: []})
                finalstate = transition.getfinalstate()
                if finalstate in accesscluster and finalstate != transition.getstartstate():
                    dependencemap[state].append(finalstate)

        independentlist = []
        keys = list(dependencemap.keys())
        keys.sort(key=lambda x: x.getstatename())

        for entry in keys:
            if not len(dependencemap[entry]):
                independentlist.append(entry)

        return independentlist

    def _ClusterTransitions(self, accesscluster):
        transitionmap = {}

        for state in accesscluster:
            for transition in state.getremote() + state.getdataack():
                cond = transition.getcond()[0] if transition.getcond() else "_"
                inmsg = transition.getinmsg() if isinstance(transition.getinmsg(), str) else \
                    transition.getinmsg().getmsgtype()

                self._AppendTransitionMap(transitionmap, transition, inmsg + cond)

            for transition in state.getaccess() + state.getevict():
                identkey = transition.getaccess()

                if transition.getstartstate() == transition.getfinalstate():
                    identkey += "_l"

                self._AppendTransitionMap(transitionmap, transition, identkey)

        transitionmap = self._ClusterNonAmbigousTrans(transitionmap)

        return transitionmap

    @staticmethod
    def _AppendTransitionMap(transitionmap, transition, identkey):
        entry = transitionmap.get(identkey, 0)
        if entry:
            entry.append(transition)
        else:
            transitionmap.update({identkey: [transition]})

    @staticmethod
    def _ClusterNonAmbigousTrans(transitionmap):
        match = 1

        for transitionkey in sorted(transitionmap.keys()):
            finalstates = []
            for transition in transitionmap[transitionkey]:
                finalstate = transition.getfinalstate()
                if transition.getstartstate() != finalstate:
                    finalstates.append(finalstate)

            if len(list(set(finalstates))) > 1:
                match = 0
                break

        if match == 0:
            return {}

        return transitionmap

    @staticmethod
    def _RemoveSingleEntries(statedict):
        removeguards = []
        for guard in statedict:
            if len(statedict[guard]) == 1:
                removeguards.append(guard)

        for guard in removeguards:
            del statedict[guard]

        return statedict


