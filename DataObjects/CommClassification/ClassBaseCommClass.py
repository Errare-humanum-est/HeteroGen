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

from typing import List
from Debug.Monitor.ClassDebug import Debug
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2


class CommClassState(Debug):

    def __init__(self):
        Debug.__init__(self)
        # First CommClass analysis must be performed
        self.access_miss = []
        self.access_hit = []

        self.evict_miss = []
        self.evict_hit = []

        self.event_miss = []
        self.event_hit = []

        self.remote_miss = []
        self.remote_hit = []

        self.resp_ack = []

    # Depends on the communication classification
    def add_classify_trans(self, transition: Transition_v2):
        self.classify_trans(transition, 'append')

    def remove_classify_trans(self, transition: Transition_v2):
        self.classify_trans(transition, 'remove')

    def classify_trans(self, transition: Transition_v2, method: str):
        if transition.comm_class == BaseCommClass.acc_req:
            getattr(self.access_miss, method)(transition)
        elif transition.comm_class == BaseCommClass.acc:
            getattr(self.access_hit, method)(transition)
        elif transition.comm_class == BaseCommClass.evi_req:
            getattr(self.evict_miss, method)(transition)
        elif transition.comm_class == BaseCommClass.evi:
            getattr(self.evict_hit, method)(transition)
        elif transition.comm_class == BaseCommClass.evnt_req:
            getattr(self.event_miss, method)(transition)
        elif transition.comm_class == BaseCommClass.evnt_resp or transition.comm_class == BaseCommClass.evnt:
            getattr(self.event_hit, method)(transition)
        elif transition.comm_class == BaseCommClass.rem_req:
            getattr(self.remote_miss, method)(transition)
        elif transition.comm_class == BaseCommClass.rem_resp or transition.comm_class == BaseCommClass.rem:
            getattr(self.remote_hit, method)(transition)
        elif transition.comm_class == BaseCommClass.resp_resp or transition.comm_class == BaseCommClass.resp:
            getattr(self.resp_ack, method)(transition)

    def getaccess(self) -> List[Transition_v2]:
        return self.access_hit + self.access_miss

    def getaccesshit(self) -> List[Transition_v2]:
        return self.access_hit

    def getaccessmiss(self) -> List[Transition_v2]:
        return self.access_miss

    def getevict(self) -> List[Transition_v2]:
        return self.evict_hit + self.evict_miss

    def getevictmiss(self) -> List[Transition_v2]:
        return self.evict_miss

    def getremote(self) -> List[Transition_v2]:
        return self.remote_hit + self.remote_miss

    def getremotemiss(self) -> List[Transition_v2]:
        return self.remote_miss

    def getdataack(self) -> List[Transition_v2]:
        return self.resp_ack


class BaseCommClass:

    undef = "undefined"

    acc = "access_hit"
    evi = "evict_hit"

    local = (acc, evi)

    acc_req = "access_request"
    evi_req = "evict_request"

    acc_evnt = "access_event"
    evi_evnt = "evict_event"

    acc_req_evnt = "access_request_event"
    evi_req_evnt = "evict_request_event"

    access_summary = (acc_req, evi_req)

    evnt = "event"
    evnt_ack = "event_ack"
    evnt_req = "event_request"
    evnt_resp = "event_response"

    evnt_summary = (evnt, evnt_req, evnt_resp)

    rem = "remote"
    rem_req = "remote_request"          # Currently no distinction between remote_request and remote_response
    rem_resp = "remote_response"
    rem_evnt = "remote_event"

    rem_summary = (rem, rem_req, rem_resp, rem_evnt)

    resp = "response"
    resp_req = "response_request"
    resp_resp = "response_response"     # Currently no distinction between response_request and response_response
    resp_event = "response_event"

    resp_summary = (resp, resp_req, resp_resp, resp_event)
