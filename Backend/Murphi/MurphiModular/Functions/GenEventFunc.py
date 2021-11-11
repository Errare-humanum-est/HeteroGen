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

from typing import List, Set

from DataObjects.ClassCluster import Cluster
from DataObjects.FlowDataTypes.ClassEvent import Event, EventAck
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture

from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Murphi.MurphiModular.General.GenAtomicEvent import AtomicEvent
from Backend.Murphi.BaseConfig import BaseConfig

from Debug.Monitor.ClassDebug import Debug


class GenEventFunc(TemplateHandler, Debug):

    def __init__(self, murphi_str: List[str], clusters: List[Cluster], config: BaseConfig):
        TemplateHandler.__init__(self)
        Debug.__init__(self)

        event_func_str = []
        event_archs: Set[FlatArchitecture] = set()

        for cluster in clusters:
            machines = set(cluster.system_tuple)

            for arch in set([machine.arch for machine in machines]):
                for transition in arch.get_architecture_transitions():
                    if isinstance(transition.guard, Event) or isinstance(transition.guard, EventAck):
                        event_func_str.append(self.gen_evt_func(arch, config) + self.nl)
                        if config.atomic_events:
                            event_func_str.append(self.gen_evt_atomic_func(arch) + self.nl)
                        event_archs.add(arch)
                        break

        if event_archs:
            event_func_str.append(self.gen_evt_reset_func(event_archs))

        murphi_str.append("----" + __name__.replace('.','/') + self.nl + self.add_tabs("".join(event_func_str), 1))

    def gen_evt_func(self, arch: FlatArchitecture, config: BaseConfig) -> str:
        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_event_func_general),
                                    [str(arch),
                                     MurphiTokens.k_event_label,
                                     MurphiTokens.k_obj_set,
                                     MurphiTokens.k_address,
                                     MurphiTokens.k_instance,
                                     "undefine evt_entry." + AtomicEvent.atomic_event_lock_var
                                     if config.atomic_events else ""
                                     ])

    def gen_evt_atomic_func(self, arch: FlatArchitecture) -> str:
        return self._stringReplKeys(self._openTemplate(AtomicEvent.f_atomic_event_func_template),
                                    [AtomicEvent.test_atomic_event_func,
                                     AtomicEvent.lock_atomic_event_func,
                                     AtomicEvent.unlock_atomic_event_func,
                                     str(arch),
                                     MurphiTokens.k_instance,
                                     MurphiTokens.k_obj_set,
                                     MurphiTokens.k_address,
                                     AtomicEvent.atomic_event_lock_var
                                     ])

    def gen_evt_reset_func(self, event_archs: Set[FlatArchitecture]):
        event_arch_reset_body = ""

        for event_arch in event_archs:
            event_arch_reset_body += MurphiTokens.k_reset_event + str(event_arch) + "()" + self.end

        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_reset_func),
                                    [MurphiTokens.k_reset_event, self.add_tabs(event_arch_reset_body, 1)])
