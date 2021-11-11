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

from typing import Tuple, List, Dict, Set
from DataObjects.States.ClassStatev2 import State_v2

from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture

from Debug.Monitor.ClassDebug import Debug


class ArchTupleStateOrdering:

    def __init__(self, arch_tuple: Tuple[FlatArchitecture]):
        Debug.perror("ArchTupleOrdering requires architectures to be unique, duplicates are not permitted",
                     len(arch_tuple) == len(set(arch_tuple)))
        self.arch_tuple: Tuple[FlatArchitecture] = arch_tuple
        self.arch_state_dict: Dict[FlatArchitecture, Set[State_v2]] = {}
        self.update_arch_state_dict()

    def update_arch_state_dict(self):
        for arch in self.arch_tuple:
            self.arch_state_dict[arch] = set()
            for state in arch.get_architecture_states():
                self.arch_state_dict[arch].add(state)

    def sort_states_by_architecture(self, states: List[State_v2]) -> Tuple[State_v2]:
        sorted_state_list: List[State_v2] = []
        for arch in self.arch_tuple:
            sorted_state_list.append(self.find_state_in_architecture(arch, states))
        Debug.perror("Passed state number is unequal the number of architectures",
                     len(sorted_state_list) == len(self.arch_tuple))
        return tuple(sorted_state_list)

    def find_state_in_architecture(self, arch: FlatArchitecture, states: List[State_v2]) -> State_v2:
        for state in states:
            if state in self.arch_state_dict[arch]:
                return state
        Debug.perror("No state found for architecture: " + str(arch))

    def get_arch_by_state(self, state: State_v2) -> FlatArchitecture:
        for arch in self.arch_state_dict:
            if state in self.arch_state_dict[arch]:
                return arch
        Debug.perror("Architecture containing state not found: " + str(state))
