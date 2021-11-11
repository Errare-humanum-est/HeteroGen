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

from typing import Dict, Union, Set


class Event:
    def __init__(self, name):
        assert isinstance(name, str)
        self.type = name

    def __str__(self):
        return self.type


class EventAck:
    def __init__(self, name):
        assert isinstance(name, str)
        self.type = name

    def __str__(self):
        return self.type


## EventNetwork
#
#  Events that are triggered within a machine
#  Dependency: Event, EventAck
class EventNetwork:
    def __init__(self):
        # Record event issue and acknowledgement
        self.event_issue: Dict[str, Event] = {}
        self.event_ack: Dict[str, EventAck] = {}

    def add_new_event(self, new_event: Union[Event, EventAck]) -> Union[Event, EventAck]:
        ref_dict = self.event_issue
        if type(new_event) == EventAck:
            ref_dict = self.event_ack

        if str(new_event) in ref_dict:
            return ref_dict[str(new_event)]
        else:
            ref_dict[str(new_event)] = new_event
            return new_event

    def update_event_names(self, event_to_new_event_dict: Dict[str, str]):
        self._update_event_names(self.event_issue, event_to_new_event_dict)
        self._update_event_names(self.event_ack, event_to_new_event_dict)

    def get_event_names(self) -> Set[str]:
        return set(self.event_issue.keys()).union(set(self.event_ack.keys()))

    @staticmethod
    def _update_event_names(event_dict: Dict[str, Union[Event, EventAck]], event_to_new_event_dict: Dict[str, str]):
        for event_name in event_to_new_event_dict:
            if event_name not in event_dict:
                continue
            # Update event type
            event_dict[event_name].type = event_to_new_event_dict[event_name]
            # Update dict entry
            event_dict[event_to_new_event_dict[event_name]] = event_dict[event_name]
            # Clear old dict entry
            event_dict.pop(event_name)

    def exist_events(self) -> bool:
        if self.event_issue or self.event_ack:
            return True
        return False

    def merge_event_networks(self, other: 'EventNetwork'):
        self.event_issue.update(other.event_issue)
        self.event_ack.update(other.event_ack)
