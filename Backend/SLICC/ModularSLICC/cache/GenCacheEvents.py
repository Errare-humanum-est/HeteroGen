#  Copyright (c) 2022.  Nicolai Oswald
#  Copyright (c) 2022.  University of Edinburgh
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

from typing import List, Dict, Tuple
from collections import OrderedDict
from DataObjects.Architecture.ClassBaseArchitecture import BaseArchitecture
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from Backend.SLICC.ModularSLICC.common.GenMachineEvents import GenMachineEvents
from Backend.SLICC.ModularSLICC.common import Util


class GenCacheEvents(TemplateHandler):
    template_file = "event_enumeration.sm"

    def __init__(self, handler_dir: str):
        TemplateHandler.__init__(self, handler_dir)

    def gen_cache_events_str(self, arch: BaseArchitecture, in_ports: 'OrderedDict[str, str]') -> str:

        const_str = "//" + __name__ + self.nl
        event_strs = self.gen_local_hit_events(Util.get_local_hit_events(arch))
        event_strs.append(GenMachineEvents.gen_stall_event(self, "mandatory_in"))
        for port in sorted(in_ports.values()):
            event_strs.extend(
                self.gen_remote_hit_events(port, Util.get_remote_hit_events_port(arch, port)))
            event_strs.append(f"dealloc{port}, desc=\"Event indicating the cache line + tbe should be deallocated "
                              f"following a message received on {port}.\"{self.sem}")
            event_strs.append(GenMachineEvents.gen_stall_event(self, port))

        next_states = {str(state) for state in Util.get_states_following_invalid_states(arch)}
        for next_state in sorted(next_states):
            event_strs.append(f"alloc{next_state}, "
                              f"desc=\"Event indicating cache entry alloc before moving to {next_state}.\"{self.sem}"
                              )

        event_strs.append(GenMachineEvents.gen_tbe_alloc_event(self))
        event_strs.append(GenMachineEvents.gen_tbe_dealloc_event(self))
        event_strs.append(GenMachineEvents.gen_progress_event(self))

        events_str = self.nl.join(event_strs)

        # events_str = GenMachineEvents.gen_events_str(self, level.cache)
        const_str += self.string_repl_keys(self.open_template(GenCacheEvents.template_file),
                                           ["Cache", self.add_tabs(events_str, 1)]
                                           )

        return const_str + self.nl

    def gen_local_hit_events(self, hit_map: Dict[Tuple[str, str], Tuple[str, str]]) -> List[str]:
        event_strs = []
        for (access, start_state), (end_state, event_name) in sorted(hit_map.items()):
            event_strs.append(
                f"{event_name}, desc=\"{start_state}->{end_state} upon local {access} hit.\"{self.sem}")

        return event_strs

    def gen_remote_hit_events(self, port: str, hit_map: Dict[Tuple[str, str], str]) -> List[str]:
        event_strs = []
        for (access, end_state), event_name in sorted(hit_map.items()):
            event_strs.append(
                f"{event_name}, desc=\"Remote {access} hit ending in state {end_state}. Should pop {port}.\"{self.sem}"
            )

        return event_strs
