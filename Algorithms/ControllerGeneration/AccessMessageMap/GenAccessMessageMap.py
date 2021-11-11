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

from typing import Tuple, Set, List, Dict, Union

from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.ClassLevel import Level
from DataObjects.ClassMultiDict import MultiDict

from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess
from DataObjects.FlowDataTypes.ClassMessage import Message, BaseMessage
from DataObjects.ClassTrace import Trace


class GenAccessMessageMap:

    auto_detect_access_appearance_at_memory: bool = True

    def __init__(self, level: Level):

        self.level = level

        # Step 1) Determine states that can do silent upgrades and what access permissions they have.
        self.stable_state_immediate_access_map = MultiDict()
        self.det_immediate_access_map()

        ### HeteroGen
        # Step 2)
        self.state_to_memory_write_message_map: Dict[State_v2, MultiDict[BaseMessage]] = MultiDict()
        if self.auto_detect_access_appearance_at_memory:
            # If an access related to a remote message can be detected in a cache state, then the cache data is visible
            # to memory, however, if a remote cache performs an accesses that never notifies the current cache,
            # then this cache data is not visible to memory.
            self.det_memory_write_access()

        # Step 3) Determine which BaseMessages have to be renamed by having the cache communicating to the dir
        self.cache_to_dir_state_base_message_map: List[Tuple[Trace, BaseMessage, Trace]] = []       # HeteroGen
        self.det_cache_directory_messages()

        # Step 4) Generate new base messages and map these to the accesses
        self.cache_state_to_new_base_message_map: Dict[State_v2, BaseMessage] = {}
        self.new_to_original_base_message_map: Dict[BaseMessage, BaseMessage] = {}
        self.dir_state_base_message_access_map: Dict[State_v2, Dict[BaseMessage, BaseAccess.Access]] = {}

        # Use this Dict to track all messages and to which new base messages they need to be assigned
        self.message_to_new_base_message_map: Dict[Message, BaseMessage] = {}

        self.gen_new_base_messages_and_map_to_accesses()

        # Step 5)

        ### HieraGen also needs to know accesses associated with observed remote messages
        self.cache_fwd_trace_to_remote_access_map = {}
        #self.det_fwd_request_access()

    def det_immediate_access_map(self):
        for cache_state in self.level.cache.state_sub_tree_dict:
            self.stable_state_immediate_access_map[cache_state] = []
            trans_traces = []
            for sub_tree in self.level.cache.state_sub_tree_dict[cache_state]:
                trans_traces += self.level.cache.get_trans_traces(sub_tree, cache_state, self.level.cache.stable_states)
            for trans_trace in trans_traces:
                trans_trace = Trace(trans_trace)
                # If a cache can perform an load or store access without notifying the outside world it has access
                # permissions, special accesses like acquire are and release are only supersets of loads and stores.
                # Events(Fences) only gen_make read and writes visible
                if isinstance(trans_trace.init_guard, BaseAccess.Access) and \
                        str(trans_trace.init_guard) in BaseAccess.Access_str_list \
                        and not trans_trace.out_msg:
                    if trans_trace.init_guard not in self.stable_state_immediate_access_map:
                        self.stable_state_immediate_access_map[cache_state] = trans_trace.init_guard

    def det_memory_write_access(self):
        for system_tuple in self.level.state_tuple_list:
            access_cache_trace = system_tuple.get_arch_access_trace(self.level.cache.get_flat_base_architecture())
            if len(access_cache_trace) > 1:
                continue
            access_cache_trace = access_cache_trace[0]

            remote_cache_traces = system_tuple.get_arch_traces(self.level.cache.get_flat_base_architecture())
            remote_cache_traces.remove(access_cache_trace)

            dir_trace = system_tuple.get_arch_traces(self.level.directory.get_flat_base_architecture())
            if not dir_trace:
                continue
            dir_trace = dir_trace[0]

            access_cache_in_messages_set = set(self.get_base_messages_trace(access_cache_trace.guards_msg))
            access_cache_out_messages_set = set(self.get_base_messages_trace(access_cache_trace.out_msg))
            dir_in_base_messages_set = set(self.get_base_messages_trace(dir_trace.guards_msg))
            dir_out_base_messages_set = set(self.get_base_messages_trace(dir_trace.out_msg))

            for remote_cache_trace in remote_cache_traces:
                if not self.check_store_permission_trace_start_state(remote_cache_trace):
                    continue

                remote_cache_in_messages_set = set(self.get_base_messages_trace(remote_cache_trace.guards_msg))
                remote_cache_out_message_set = set(self.get_base_messages_trace(remote_cache_trace.out_msg))

                if (not self.check_cache_to_remote_cache_request(access_cache_out_messages_set,
                                                                 remote_cache_in_messages_set) and
                        not self.check_dir_to_remote_cache_request(dir_out_base_messages_set,
                                                                   remote_cache_in_messages_set)):
                    continue

                if (self.check_remote_cache_to_cache_response(remote_cache_out_message_set,
                                                              access_cache_in_messages_set) or
                        (self.check_remote_cache_to_dir_response(remote_cache_out_message_set,
                                                                 dir_in_base_messages_set) and
                         self.check_dir_to_cache_response(dir_out_base_messages_set, access_cache_in_messages_set))):

                    if (not remote_cache_trace.start_state in self.state_to_memory_write_message_map or
                            not dir_trace.init_guard in
                                self.state_to_memory_write_message_map[remote_cache_trace.start_state]):
                        self.state_to_memory_write_message_map[remote_cache_trace.start_state] = \
                            dir_trace.init_guard

    @staticmethod
    def check_cache_to_remote_cache_request(access_cache_out_messages_set, remote_cache_in_messages_set):
        return access_cache_out_messages_set.intersection(remote_cache_in_messages_set)

    @staticmethod
    def check_dir_to_remote_cache_request(dir_out_base_messages_set, remote_cache_in_messages_set):
        return dir_out_base_messages_set.intersection(remote_cache_in_messages_set)

    def check_remote_cache_to_cache_response(self, remote_cache_out_message_set, access_cache_in_messages_set):
        return self.check_out_msgs_have_data(remote_cache_out_message_set.intersection(access_cache_in_messages_set))

    def check_remote_cache_to_dir_response(self, remote_cache_out_message_set, dir_in_base_messages_set):
        return self.check_out_msgs_have_data(remote_cache_out_message_set.intersection(dir_in_base_messages_set))

    def check_dir_to_cache_response(self, dir_out_base_messages_set, remote_cache_out_message_set):
        return self.check_out_msgs_have_data(dir_out_base_messages_set.intersection(remote_cache_out_message_set))

    @staticmethod
    def check_out_msgs_have_data(remote_msg_set: Set[Union[Message, BaseMessage]]) -> bool:
        for out_msg in remote_msg_set:
            if isinstance(out_msg, Message) or isinstance(out_msg, BaseMessage):
                return out_msg.has_data()
        return False

    def check_store_permission_trace_start_state(self, remote_cache_trace: Trace) -> bool:
        if (remote_cache_trace.start_state in self.stable_state_immediate_access_map and
                [access for access in self.stable_state_immediate_access_map[remote_cache_trace.start_state]
                 if str(access) == BaseAccess.k_store]):
            return True
        return False

    def det_cache_directory_messages(self):
        # Detect all messages a cache sends to the directory
        for system_tuple in self.level.state_tuple_list:
            cache_traces = system_tuple.get_arch_traces(self.level.cache.get_flat_base_architecture())
            dir_trace = system_tuple.get_arch_traces(self.level.directory.get_flat_base_architecture())
            if not dir_trace:
                continue
            dir_trace = dir_trace[0]

            for cache_trace in cache_traces:
                if not cache_trace.trace_trans:
                    continue
                cache_out_base_messages_set = set(self.get_base_messages_trace(cache_trace.out_msg))
                dir_in_base_messages_set = set(self.get_base_messages_trace(dir_trace.guards_msg))
                for msg_match in cache_out_base_messages_set.intersection(dir_in_base_messages_set):

                    new_dir_state_base_message_tuple = (cache_trace, msg_match, dir_trace)

                    if new_dir_state_base_message_tuple not in self.cache_to_dir_state_base_message_map:
                        self.cache_to_dir_state_base_message_map.append(new_dir_state_base_message_tuple)

    @staticmethod
    def get_base_messages_trace(msg_list: List[Union[Message, BaseMessage, BaseAccess.Access]]) -> List[BaseMessage]:
        base_msg_list = []
        for msg in msg_list:
            if isinstance(msg, BaseMessage):
                base_msg_list.append(msg)
            if isinstance(msg, Message):
                base_msg_list.append(msg.base_msg)
        return base_msg_list

    def gen_new_base_messages_and_map_to_accesses(self):
        # List[Tuple[Trace, BaseMessage, Trace]]

        # Filter the messages that do not need to be renamed, this is the case if a certain message is unique to a
        # specific access and state
        for cache_dir_tuple in self.cache_to_dir_state_base_message_map:
            # Determine access related to message
            dir_state = cache_dir_tuple[2].start_state
            access = self.get_trace_related_access(cache_dir_tuple[0])

            if not access:
                continue

            orig_base_message = cache_dir_tuple[1]
            base_message = orig_base_message
            # The first message corresponding to a specific access does not need to be renamed
            if (dir_state in self.dir_state_base_message_access_map and
                    base_message in self.dir_state_base_message_access_map[dir_state] and
                    access != self.dir_state_base_message_access_map[dir_state][base_message] and
                    str(access) not in BaseAccess.Access_str_list):
                # Generate new base message
                base_message = self.gen_new_base_message(cache_dir_tuple[1], access)

                self.cache_state_to_new_base_message_map[cache_dir_tuple[0].start_state] = base_message
                self.new_to_original_base_message_map[base_message] = orig_base_message

            if dir_state not in self.dir_state_base_message_access_map:
                self.dir_state_base_message_access_map[dir_state] = {}

            self.dir_state_base_message_access_map[dir_state][base_message] = access

    def get_trace_related_access(self, cache_trace: Trace) -> BaseAccess.Access:
        if isinstance(cache_trace.init_guard, BaseAccess.Access):
            if str(cache_trace.init_guard) not in BaseAccess.Access_str_list:
                return cache_trace.init_guard       # acquire, release, mfence, .....

            # The state is not a memory write state, so all the writes access permission request won't become visible
            # when fetching the data, hence it is only necessary to convey load access permissions to the directory
            access = self.get_optimized_access(cache_trace)
            if access:
                return access

            # If the memory write states cannot be determined, assume the worst case that every state is a memory write
            # state
            silent_store = [access for access in self.stable_state_immediate_access_map[cache_trace.final_state]
                            if str(access) == BaseAccess.k_store]

            if silent_store:
                return silent_store[0]          # store access
            return cache_trace.init_guard       # load access

        else:
            # The state is a memory write state, so all the writes are already visible to memory, hence it is not
            # necessary to convey the access to the directory
            if (self.state_to_memory_write_message_map and 
                    cache_trace.start_state in self.state_to_memory_write_message_map):
                return None

            # No access request trace, convey maximum access permission for start state. The
            # remote trace could be a write back / write commit or an evict write back
            silent_store = [access for access in self.stable_state_immediate_access_map[cache_trace.start_state]
                            if str(access) == BaseAccess.k_store]

            if silent_store:
                return silent_store[0]          # store write back
            else:
                # Update based protocols could have events forcing the cache blocks to update, so check if an access
                # exists in the trace final state
                if self.stable_state_immediate_access_map[cache_trace.final_state]:
                    silent_store = [access for access in self.stable_state_immediate_access_map[cache_trace.final_state]
                                    if str(access) == BaseAccess.k_store]
                    silent_load = [access for access in self.stable_state_immediate_access_map[cache_trace.final_state]
                                   if str(access) == BaseAccess.k_load]

                    if silent_store:
                        return silent_store[0]  # store write back
                    else:
                        return silent_load[0]
                else:
                    return None

    def get_optimized_access(self, cache_trace: Trace):
        if self.auto_detect_access_appearance_at_memory:
            # If the cache access request trace final state is a memory write state, then it must be identified as such
            if (self.state_to_memory_write_message_map and
                    cache_trace.final_state in self.state_to_memory_write_message_map):
                return None

            # The state is not a memory write state, so return
            if str(cache_trace.init_guard) == BaseAccess.k_load:
                return cache_trace.init_guard

            silent_load = [access for access in self.stable_state_immediate_access_map[cache_trace.final_state]
                           if str(access) == BaseAccess.k_load]

            if silent_load:
                return silent_load[0]
        return None

    def gen_new_base_message(self, cur_base_msg: BaseMessage, access: BaseAccess.Access):
        new_base_message = BaseMessage(cur_base_msg.id + str(access), cur_base_msg.msg_type, cur_base_msg.vc)
        return self.level.global_arch.network.add_new_base_message(new_base_message)

    ####################################################################################################################
    # Hierarchical Functions
    ####################################################################################################################
