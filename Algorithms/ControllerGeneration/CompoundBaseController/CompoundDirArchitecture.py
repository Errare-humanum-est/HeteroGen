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

from typing import List

from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.ClassLevel import Level

from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from Algorithms.ControllerGeneration.AccessMessageMap.GenAccessMessageMap import GenAccessMessageMap
from DataObjects.FlowDataTypes.ClassMessage import Message, BaseMessage
from DataObjects.ClassMultiDict import MultiDict
from Debug.Monitor.ClassDebug import Debug
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess


class CompoundDirArchitecture(FlatArchitecture, GenAccessMessageMap):

    def __init__(self, arch_level: Level, gdbg: bool = False):
        self.cache = arch_level.cache
        self.directory = arch_level.directory

        # Determine message mappings
        GenAccessMessageMap.__init__(self, arch_level)

        # Update the cache transitions
        self.update_cache_transitions()

        ## Generate new directory transitions, if exist multiple messages that are related to different accesses, but
        #  share the same message identifier
        new_transitions = self.gen_new_directory_transitions()

        FlatArchitecture.__init__(self, self.directory, gdbg)
        FlatArchitecture.copy_flat_architecture(self, self.directory)
        if new_transitions:
            self.update_base_fsm(self.directory.init_state, self.directory.stable_states, list(new_transitions))

        # Register the new proxy directory controller as the directory of the level replacing the previous directory
        arch_level.directory = self

    def __str__(self):
        return str(self.arch_name)

    ####################################################################################################################
    # Update cache transitions
    ####################################################################################################################
    # In cache transitions the base messages can be simply replaced and the operation strings updated. This is possible,
    # as the number of transitions stays the same and only the type of access is encoded in the message
    def update_cache_transitions(self):
        for state in self.cache_state_to_new_base_message_map:
            new_base_message = self.cache_state_to_new_base_message_map[state]
            old_base_message = self.new_to_original_base_message_map[new_base_message]
            access = set([self.dir_state_base_message_access_map[dir_state][new_base_message]
                          for dir_state in self.dir_state_base_message_access_map.keys()])
            if len(access) > 1:
                Debug.perror('More than one access type detected')
            access = list(access)[0]
            for transition_tree in self.cache.state_sub_tree_dict[state]:
                base_transition = self.get_transitions_by_start_state(transition_tree, state)[0]

                # Only accesses related to the special operations are renamed
                if isinstance(base_transition.guard, BaseAccess.Access) and base_transition.guard != access:
                    continue

                for transition in self.get_transitions_from_graph(transition_tree):
                    self.update_transition_base_messages(transition, old_base_message, new_base_message)

    ####################################################################################################################
    # Update and copy directory transitions
    ####################################################################################################################
    # In case of the directory, it is not enough to simply update the transitions, as the number of different messages
    # has changed on the cache side. While messages like ABC_load and ABC_store still have the same the same
    # functionality coherence wise, they convey another access that is performed by the cache to the directory, which
    # can forward the access now to another controller to build Hierachies or HeteroGenous architectures
    def gen_new_directory_transitions(self):
        old_to_new_base_message_multidict = self.gen_old_to_new_base_message_multidict()
        if not old_to_new_base_message_multidict:
            return None
        new_transitions: List[Transition_v2] = []
        # Only the guard messages need to be renamed, as only the cache conveys information
        for transition in self.directory.get_architecture_transitions():
            if not (isinstance(transition.guard, Message) or isinstance(transition.guard, BaseMessage)):
                continue
            cur_base_msg = transition.guard if isinstance(transition.guard, BaseMessage) else transition.guard.base_msg

            if cur_base_msg in old_to_new_base_message_multidict:
                for new_base_msg in old_to_new_base_message_multidict[cur_base_msg]:
                    new_trans = transition.deepcopy_trans()
                    self.update_transition_base_messages(new_trans, cur_base_msg, new_base_msg)
                    new_transitions.append(new_trans)
                    new_trans.start_state.add_transition(new_trans)
        return self.directory.get_architecture_transitions().union(set(new_transitions))

    def gen_old_to_new_base_message_multidict(self):
        old_to_new_base_message_list = MultiDict()
        for new_base_message in self.new_to_original_base_message_map:
            old_to_new_base_message_list[self.new_to_original_base_message_map[new_base_message]] = new_base_message
        return old_to_new_base_message_list

    def update_transition_base_messages(self, transition: Transition_v2,
                                        old_base_message: BaseMessage, new_base_message: BaseMessage):
        transition.guard = self.update_message(transition.guard, old_base_message, new_base_message)
        out_msgs = []
        for out_msg in transition.out_msg:
            out_msgs.append(self.update_message(out_msg, old_base_message, new_base_message))
        transition.out_msg = out_msgs
        transition.rename_operation(str(old_base_message), str(new_base_message))

    @staticmethod
    def update_message(guard, old_base_message: BaseMessage, new_base_message: BaseMessage):
        if isinstance(guard, Message) and guard.base_msg == old_base_message:
            guard.base_msg = new_base_message
            return guard
        elif isinstance(guard, BaseMessage) and guard == old_base_message:
            return new_base_message
        else:
            return guard

        # The architecture is
    def get_arch_list(self):
        return [self, self.cache, self.directory]

    def merge_machine_definitions(self):
        # Update the machine definition of the proxy machine
        Debug.perror("Unable to generate proxy cache. Variables in cache and directory have identical identifiers",
                     set(self.directory.machine.variables.keys()).intersection(
                         self.cache.machine.variables))
        self.directory.machine.variables.update(self.cache.machine.variables)
        self.directory.machine.variables_init_val.update(
            self.cache.machine.variables_init_val)
        # Update the machine event definitions from the proxy cache
        Debug.perror("Unable to generate proxy cache. Events in cache and directory have identical identifiers",
                     set(self.directory.machine.variables.keys()).intersection(
                         self.cache.machine.variables))
        self.directory.event_network.event_issue.update(
            self.cache.event_network.event_issue)
        self.directory.event_network.event_ack.update(
            self.cache.event_network.event_ack)

    ####################################################################################################################
    # Hierarchical Functions
    ####################################################################################################################
    def get_flat_base_architecture(self):
        return self.directory
