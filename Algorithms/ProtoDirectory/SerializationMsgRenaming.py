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

from typing import List, Dict, Tuple, Union, Set, FrozenSet

from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess, Access, Evict
from DataObjects.ClassSystemTuple import SystemTuple
from DataObjects.FlowDataTypes.ClassMessage import Message, BaseMessage
from DataObjects.States.ClassStatev2 import State_v2
from Parser.DataTypes.ClassGuard import Guard

from Algorithms.ControllerGeneration.NetworkxGeneral.TreeCopyNetworkx import TreeCopyNetworkx

from Debug.Monitor.ClassDebug import Debug


class SerializationMsgRenaming(BaseAccess, TreeCopyNetworkx, Debug):
    def __init__(self,
                 allowed_state_tuples: Dict[SystemTuple, SystemTuple],
                 cache: FlatArchitecture,
                 directory: FlatArchitecture):
        BaseAccess.__init__(self)
        TreeCopyNetworkx.__init__(self)
        Debug.__init__(self, True)

        self.cache = cache
        self.directory = directory

        # Generate the silent state sets set
        silent_state_sets_set, state_connectivity_sets_set = self.gen_logical_cache_state_sets(cache)
        # Identify the possible directory states for the state sets
        cache_directory_state_set_map = self.gen_directory_cache_state_set_map(allowed_state_tuples,
                                                                               silent_state_sets_set)

        # Identify message name conflicts
        self.check_message_id_conflicts(state_connectivity_sets_set, cache_directory_state_set_map)

    def gen_logical_cache_state_sets(self, cache: FlatArchitecture) -> Tuple[Set[FrozenSet[State_v2]],
                                                                             Set[FrozenSet[State_v2]]]:
        # Cluster states, identifying silent upgrades
        silent_state_sets_set: Set[FrozenSet[State_v2]] = set()
        # Identifies the connectivity of the cache states
        state_connectivity_sets_set: Set[FrozenSet[State_v2]] = set()

        for state in cache.state_trans_trace_dict:
            for trace in cache.state_trans_trace_dict[state]:
                if isinstance(trace.init_guard, BaseAccess.Access_type):
                    if trace.out_msg:
                        if trace.start_state == trace.final_state:
                            continue
                        update_set = {frozenset([trace.start_state]), frozenset([trace.final_state])}
                        silent_state_sets_set.update(update_set)
                        state_connectivity_sets_set.add(frozenset((trace.start_state, trace.final_state)))
                    else:
                        silent_state_sets_set.add(frozenset((trace.start_state, trace.final_state)))

        # Identify and prune subsets
        remove_silent_state_set_sets: Set[FrozenSet[State_v2]] = set()
        for first_state_set in silent_state_sets_set:
            for second_state_set in silent_state_sets_set:
                if first_state_set == second_state_set:
                    continue
                if second_state_set.issubset(first_state_set):
                    remove_silent_state_set_sets.add(second_state_set)

        silent_state_sets_set = silent_state_sets_set - remove_silent_state_set_sets
        # Aggregate sets if they have an intersection
        silent_state_sets_set = self._aggregate_state_sets(silent_state_sets_set)

        state_connectivity_sets_set = state_connectivity_sets_set - silent_state_sets_set

        return silent_state_sets_set, state_connectivity_sets_set

    @staticmethod
    def _aggregate_state_sets(silent_state_sets_set: Set[FrozenSet[State_v2]]) -> Set[FrozenSet[State_v2]]:
        new_silent_state_sets_list = [set(silent_state_set) for silent_state_set in silent_state_sets_set]
        new_intersect_found = True
        while new_intersect_found:
            new_intersect_found = False
            for new_silent_state_set in new_silent_state_sets_list:
                for silent_state_set in silent_state_sets_set:
                    if (new_silent_state_set.intersection(silent_state_set) and
                            not new_silent_state_set.issuperset(silent_state_set)):
                        new_silent_state_set.update(silent_state_set)
                        new_intersect_found = True

        return set([frozenset(state_set) for state_set in new_silent_state_sets_list])

    def gen_directory_cache_state_set_map(self,
                                          allowed_state_tuples: Dict[SystemTuple, SystemTuple],
                                          state_sets_set: Set[FrozenSet[State_v2]]) -> Dict[FrozenSet, Set[State_v2]]:
        cache_directory_state_set_map: Dict[FrozenSet, Set[State_v2]] = {}
        for state_set in state_sets_set:
            directory_state_set = set()
            for state in state_set:
                for allowed_state_tuple in allowed_state_tuples:
                    cache_trace_list = allowed_state_tuple.get_arch_traces(self.cache)
                    directory_trace_list = allowed_state_tuple.get_arch_traces(self.directory)
                    # Only if direct mapping exists between cache and directory state
                    if len(directory_trace_list) != 1:
                        continue

                    if state in [trace.start_state for trace in cache_trace_list]:
                        directory_state_set.add(directory_trace_list[0].start_state)
                    if state in [trace.final_state for trace in cache_trace_list]:
                        directory_state_set.add(directory_trace_list[0].final_state)

            if directory_state_set:
                cache_directory_state_set_map[state_set] = directory_state_set

        return cache_directory_state_set_map

    def check_message_id_conflicts(self,
                                   state_connectivity_sets_set: Set[FrozenSet[State_v2]],
                                   cache_directory_state_set_map: Dict[FrozenSet[State_v2], Set[State_v2]]):
        # Detect message conflicts
        for state_pair in [list(state_set) for state_set in state_connectivity_sets_set]:
            self.perror("Length of connectivity set is greater than two", len(state_pair) == 2)

            first_msg_set = set([str(trans.guard) for trans in state_pair[0].state_trans
                                 if str(trans.guard) in self.cache.global_arch.network.base_message_dict])
            second_msg_set = set([str(trans.guard) for trans in state_pair[1].state_trans
                                  if str(trans.guard) in self.cache.global_arch.network.base_message_dict])

            msg_conflicts = first_msg_set.intersection(second_msg_set)

            if msg_conflicts:
                self.resolve_message_conflicts(msg_conflicts, state_pair, cache_directory_state_set_map)

    def resolve_message_conflicts(self, conflict_msg_set: Set[str], conflict_states: List[State_v2],
                                  cache_directory_state_set_map: Dict[FrozenSet[State_v2], Set[State_v2]]):
        for conflict_msg in conflict_msg_set:
            base_messages = self.cache.global_arch.network.base_message_dict[conflict_msg]
            base_msg_str = str(base_messages[0])
            for conflict_state in conflict_states:
                # Make new base messages to resolve the conflict
                base_messages_substitution_dict = self.make_new_base_messages(base_messages, conflict_state)

                for cache_state_set in cache_directory_state_set_map:
                    if conflict_state not in cache_state_set:
                        continue

                    for state in cache_state_set:
                        for transition in state.state_trans:
                            if str(transition.guard) == base_msg_str:
                                transition.guard = self.update_message_base_message(transition.guard,
                                                                                    base_messages_substitution_dict)
                                # Update the new message name in all transition operations
                                transition.rename_operation(base_msg_str, str(transition.guard))

                    for state in cache_directory_state_set_map[cache_state_set]:
                        for transition in state.state_trans:
                            out_msg_dict = {str(out_msg): out_msg for out_msg in transition.out_msg}
                            if base_msg_str in out_msg_dict:
                                out_msg_dict[base_msg_str] = self.update_message_base_message(
                                    out_msg_dict[base_msg_str], base_messages_substitution_dict)
                                # Update the new message name in all transition operations
                                transition.rename_operation(base_msg_str, str(out_msg_dict[base_msg_str]))

    def make_new_base_messages(self,
                               base_messages: List[BaseMessage],
                               state: State_v2) -> Dict[BaseMessage, BaseMessage]:
        base_messages_substitution_dict: Dict[BaseMessage, BaseMessage] = {}

        for base_message in base_messages:
            base_messages_substitution_dict[base_message] = BaseMessage(str(state) + "_" + str(base_message),
                                                                        base_message.msg_type,
                                                                        base_message.vc)
            self.cache.global_arch.network.add_new_base_message(base_messages_substitution_dict[base_message])
        return base_messages_substitution_dict

    def update_message_base_message(self,
                                    cur_msg: Union[Message, BaseMessage, Access, Evict, Guard],
                                    base_messages_substitution_dict: Dict[BaseMessage, BaseMessage]):
        if isinstance(cur_msg, Message):
            cur_base_msg = cur_msg.base_msg
            cur_base_msg.remove_message_object(cur_msg)
            cur_msg.base_msg = base_messages_substitution_dict[cur_base_msg]
            cur_msg.base_msg.register_message_object(cur_msg)
            return cur_msg
        elif isinstance(cur_msg, BaseMessage):
            return base_messages_substitution_dict[cur_msg]
        else:
            for base_message in base_messages_substitution_dict:
                if str(cur_msg) == str(base_message):
                    cur_msg.id = str(base_messages_substitution_dict[base_message])
                    return cur_msg
