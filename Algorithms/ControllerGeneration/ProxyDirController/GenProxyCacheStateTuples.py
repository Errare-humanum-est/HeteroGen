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

from typing import Union, List, Dict, Any

from DataObjects.ClassTrace import Trace
from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.ClassLevel import Level
from DataObjects.ClassSystemTuple import SystemTuple
from DataObjects.ClassMultiDict import MultiDict
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess
from Debug.Monitor.ClassDebug import Debug


class GenProxyCacheStateTuples(Debug):

    def __init__(self, arch_level: Level):
        Debug.__init__(self)
        self.access_system_tuples = self.gen_access_state_tuple_dict(arch_level)
        self.evict_system_tuples = self.gen_evict_state_tuple_dict(arch_level, self.access_system_tuples)

    def gen_access_state_tuple_dict(self, arch_level: Level):
        access_system_tuples: MultiDict = MultiDict()

        for state_tuple in arch_level.state_tuple_list:
            # Extract the directory trace
            ll_dir_trace = self.get_dir_trace(state_tuple, arch_level)

            # extract the cache access trace
            ll_access_trace = self.get_cache_access_trace(state_tuple, arch_level)

            # The cache access trace must exist, it must start in an initial state and the guard must be of type Access
            if (not ll_access_trace
                    or not ll_access_trace.start_state == arch_level.cache.init_state
                    or not isinstance(ll_access_trace.init_guard, BaseAccess.Access)):
                continue

            # If in case of access the directory does not need to be notified then just continue as the proxy cache is
            # memory less
            if not ll_dir_trace:
                continue

            #self.perror("No directory trace found for cache trace: " + str(ll_access_trace), ll_dir_trace)

            access_system_tuples[ll_access_trace.init_guard] = state_tuple

        return access_system_tuples

    ## Find the evict_system_tuples of the proxy cache, the evict system tuples must match the access_system_tuples
    #   The idea is that after the proxy cache performed the access (access_system_tuples) it has to evict the cache
    #   block again as the proxy cache is memory less. The correct eviction transaction must be found based on the cache
    #   state and the directory state
    def gen_evict_state_tuple_dict(self, arch_level: Level,
                                   access_system_tuples: Dict[Any, List[SystemTuple]]) \
            -> Dict[State_v2, List[SystemTuple]]:
        # After the evict the cache must return into its initial state
        evict_system_tuples: MultiDict = MultiDict()

        for guard in access_system_tuples:
            for access_system_tuple in access_system_tuples[guard]:
                for state_tuple in arch_level.state_tuple_list:
                    # Extract the directory trace
                    ll_dir_trace = self.get_dir_trace(state_tuple, arch_level)

                    # extract the cache access trace
                    ll_evict_trace = self.get_cache_access_trace(state_tuple, arch_level)

                    ll_access_trace = self.get_cache_access_trace(access_system_tuple, arch_level)

                    # The cache access trace must exist, it must start in an initial state and the guard must be of type
                    # Access
                    if (not ll_evict_trace
                            or not ll_evict_trace.start_state == ll_access_trace.final_state
                            or not isinstance(ll_evict_trace.init_guard, BaseAccess.Evict)):
                        continue

                    #self.perror("No directory trace found for cache trace: " + str(ll_evict_trace), ll_dir_trace)

                    if (ll_access_trace.final_state not in evict_system_tuples or
                            state_tuple not in evict_system_tuples[ll_access_trace.final_state]):
                        evict_system_tuples[ll_access_trace.final_state] = state_tuple

        return evict_system_tuples

    @staticmethod
    def get_dir_trace(state_tuple: SystemTuple, level: Level) -> Union[None, Trace]:
        ll_dir_trace = state_tuple.get_arch_traces(level.directory)
        if not ll_dir_trace:
            return None
        assert len(ll_dir_trace) == 1, "Multiple directory traces not supported"
        return ll_dir_trace[0]

    @staticmethod
    def get_cache_access_trace(state_tuple: SystemTuple, level: Level) -> Union[None, Trace]:
        ll_cc_trace = state_tuple.get_arch_access_trace(level.cache)
        if not ll_cc_trace:
            return None
        assert len(ll_cc_trace) == 1, "Multiple directory traces not supported"
        return ll_cc_trace[0]
