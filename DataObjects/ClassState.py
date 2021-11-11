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

from typing import List, Dict, Tuple
from antlr3.tree import CommonTree

from DataObjects.FlowDataTypes.ClassMessage import Message
from Deprecated.ClassTransition import Transition

from Debug.Monitor.ClassDebug import Debug


class State(Debug):
    def __init__(self, name, access=0, evict=0):
        Debug.__init__(self)

        self.id = id(self)

        # The more access permission the higher the index,
        # e.g. [load, store]; if store permission then also load is granted
        if isinstance(access, list):
            self.access = access
        elif isinstance(access, str):
            self.access = [access]
        else:
            self.access = []

        if isinstance(evict, list):
            self.evict = evict
        elif isinstance(evict, str):
            self.evict = [evict]
        else:
            self.evict = []

        assert isinstance(name, str)
        self.state = name

        self.state_trans: List[Transition] = []

        self.accessMiss = []
        self.accessHit = []

        self.evictMiss = []
        self.evictHit = []

        self.remoteMiss = []
        self.remoteHit = []
        self.dataAck = []

        self.start_state_set = []
        self.end_state_set = []

        self.deferredRespMsg: List[Message] = []
        self.deferredOperations: Dict[Message, List[CommonTree]] = {}

        self.inherited_remote_traces: List['Trace'] = []

    def __str__(self):
        return self.state

    def testaccess(self, access):
        if access in self.access:
            return 1
        return 0

########################################################################################################################
# STATE ID
########################################################################################################################

    def setstatename(self, name: str):
        assert isinstance(name, str)
        self.state = name

    def getstatename(self) -> str:
        return self.state

########################################################################################################################
# STATE TRANSITION
########################################################################################################################
    def addtransitions(self, transitions: [Transition, List[Transition]]) -> List[Transition]:

        hash_transition_list = [trans.get_hash() for trans in self.state_trans]
        transition_list = []
        
        if isinstance(transitions, list):
            for transition in transitions:
                if transition.get_hash() not in hash_transition_list:
                    transition_list.append(transition)
        else:
            if transitions not in hash_transition_list:
                transition_list.append(transitions)

        if transition_list:
            self.state_trans += transition_list
            self.classify_transitions(transition_list)
        return self.state_trans

    def addremotemiss(self, transition: Transition):
        self.state_trans.append(transition)
        self.remoteMiss.append(transition)

    def gettransitions(self) -> List[Transition]:
        return self.state_trans

    def classify_transitions(self, transitions: List[Transition]):
        for transition in transitions:

            if transition.comm_class == ClassCommClassFunc().local:
                if transition.access in self.access:
                    self.accessHit.append(transition)
                elif transition.access in self.evict:
                    self.evictHit.append(transition)
                else:
                    assert 0, "CLASSIFICATION ERROR"

            elif transition.comm_class == ClassCommClassFunc().acc_req:
                if transition.access in self.access:
                    self.accessMiss.append(transition)
                elif transition.access in self.evict:
                    self.evictMiss.append(transition)
                else:
                    assert 0, "CLASSIFICATION ERROR"

            elif transition.comm_class in ClassCommClassFunc().rem_summary:
                self.remoteMiss.append(transition)

            elif transition.comm_class in ClassCommClassFunc().resp_summary:
                self.dataAck.append(transition)

            else:
                self.pwarning("State could not be classified")

            '''
            access_class = TransitionClassificationFunc.gen_classification(self.access)
            if access_class == TransitionClassificationEnum.access_hit:
                self.access_hit.append(transition)
            elif access_class == TransitionClassificationEnum.access_miss:
                self.access_miss.append(transition)
            elif access_class == TransitionClassificationEnum.evict_hit:
                self.evict_hit.append(transition)
            elif access_class == TransitionClassificationEnum.evict_miss:
                self.evict_miss.append(transition)
            elif access_class == TransitionClassificationEnum.remote_miss:
                self.remote_miss.append(transition)
            elif access_class == TransitionClassificationEnum.data_ack:
                self.data_ack.append(transition)
            else:
                assert False, "State could not be classified"
                
            '''

    ####################################################################################################################
    # TRANSITION TESTING
    ####################################################################################################################

    def getaccess(self) -> List['Transition']:
        return self.accessHit + self.accessMiss

    def getaccesshit(self) -> List['Transition']:
        return self.accessHit

    def getaccessmiss(self) -> List['Transition']:
        return self.accessMiss

    def getevict(self) -> List['Transition']:
        return self.evictHit + self.evictMiss

    def getevictmiss(self) -> List['Transition']:
        return self.evictMiss

    def getremote(self) -> List['Transition']:
        return self.remoteHit + self.remoteMiss

    def getremotemiss(self) -> List['Transition']:
        return self.remoteMiss

    def getdataack(self) -> List['Transition']:
        return self.dataAck

    ####################################################################################################################
    # PROTOGEN FUNCTIONS
    ####################################################################################################################

    def gettransitionbyguard(self, guard: str) -> [int, 'Transition']:
        for transition in self.state_trans:
            if transition.getguard() == guard:
                return transition
        return 0

    def getmulttransitionsbyguard(self, guard: str) -> List['Transition']:
        rettransitions = []
        for transition in self.state_trans:
            if transition.getguard() == guard:
                rettransitions.append(transition)

        if rettransitions:
            return rettransitions
        else:
            return []

    def replaceremotestate(self, oldremotestate, newremotestate):
        for transition in self.state_trans:
            startstate = transition.getstartstate()
            finalstate = transition.getfinalstate()

            if startstate == oldremotestate:
                transition.setstartstate(newremotestate)

            if finalstate == oldremotestate:
                transition.setfinalstate(newremotestate)

    ####################################################################################################################
    # PROTOGEN FUNCTIONS
    ####################################################################################################################

    def add_inherited_traces(self, traces: List['Trace']):
        self.inherited_remote_traces += traces

    def test_inherited_trace(self, trace: 'Trace') -> bool:
        if trace in self.inherited_remote_traces:
            return True
        return False

    def filter_remote_traces(self, traces: List['Trace']) -> List['Trace']:
        inherited_trace_hashes = [hash(trace) for trace in self.inherited_remote_traces]
        return [trace for trace in traces if hash(trace) not in inherited_trace_hashes]


########################################################################################################################
# STATE SET
########################################################################################################################

    def set_start_state_set(self, state_set: 'StateSet'):
        if state_set not in self.start_state_set:
            self.start_state_set.append(state_set)

    def set_end_state_set(self, state_set: 'StateSet'):
        if state_set not in self.end_state_set:
            self.end_state_set.append(state_set)

    def remove_state_set(self, state_set: 'StateSet'):
        if state_set in self.start_state_set:
            self.start_state_set.remove(state_set)
        if state_set in self.end_state_set:
            self.end_state_set.remove(state_set)

    def getstatesets(self):
        return self.start_state_set + self.end_state_set

    def getstartstatesets(self) -> List['StateSet']:
        return self.start_state_set

    def getendstatesets(self) -> List['StateSet']:
        return self.end_state_set

########################################################################################################################
# PENDING MESSAGES
########################################################################################################################

    def getdefermessages(self) -> List[Message]:
        return self.deferredRespMsg

    def add_head_list_defer_msg_operations(self, message_tuple_list: List[Tuple[Message, List[CommonTree]]]):
        add_defer_msg_list = []

        for message_tuple in message_tuple_list:
            assert message_tuple[0] not in self.deferredRespMsg and message_tuple[0] not in add_defer_msg_list,\
                "Message deferral duplication"
            add_defer_msg_list.append(message_tuple[0])
            self.deferredOperations[message_tuple[0]] = message_tuple[1]

        self.deferredRespMsg = add_defer_msg_list + self.deferredRespMsg

    def add_tail_list_defer_msg_operations(self, message_tuple_list: List[Tuple[Message, List[CommonTree]]]):
        for message_tuple in message_tuple_list:
            assert message_tuple[0] not in self.deferredRespMsg, "Message deferral duplication"
            self.deferredRespMsg.append(message_tuple[0])
            self.deferredOperations[message_tuple[0]] = message_tuple[1]

    def get_defer_msg_operation(self) -> List[Tuple[Message, List[CommonTree]]]:
        message_defer_tuple_list = []
        for message in self.deferredRespMsg:
            message_defer_tuple_list.append((message, self.deferredOperations[message]))
        return message_defer_tuple_list

    def get_defer_msg_operations(self):
        defer_operations = []
        for msg in self.deferredRespMsg:
            for operation in self.deferredOperations[msg]:
                if operation not in defer_operations:
                    defer_operations.append(operation)
        return defer_operations

########################################################################################################################
# POST CLASSIFICATION FUNCTIONS
########################################################################################################################

    def testexclusive(self):
        for transition in self.accessHit:
            if transition.getaccess() == self.access[1]:
                return 1
        return 0

    def getnraccess(self):
        return len(self.accessMiss) + len(self.accessHit)

    def getnrremote(self):
        return len(self.remoteMiss) + len(self.remoteHit)

########################################################################################################################
# DEBUG
########################################################################################################################

    def get_access_str(self) -> List[str]:
        return self.access

    def get_evict_str(self) -> List[str]:
        return self.evict

    def pstate(self):
        return self.state

    def pbase(self):
        return "State:: Name:" + self.state + "  *Access: " + str(self.access)
