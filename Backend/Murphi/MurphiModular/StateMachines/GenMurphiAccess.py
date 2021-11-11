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

from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess
from DataObjects.ClassMultiDict import MultiDict
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2

from Backend.Murphi.BaseConfig import BaseConfig
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates

from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase

from Debug.Monitor.ClassDebug import Debug


class GenMurphiAccess(TemplateHandler):

    # PermFuncNames
    k_perm = "Perm_"
    f_clear_perm = "Clear_perm"
    f_set_perm = "Set_perm"
    f_exe_cpu_access = "Serve_CPU"
    f_exe_store = "Store"

    def __init__(self, arch: FlatArchitecture, config: BaseConfig):
        TemplateHandler.__init__(self)
        self.arch = arch
        self.config = config
        # A state permission is valid if a transition triggered by this access exists, that doesn't have an outgoing
        #  edge
        self.state_permission_map: MultiDict = MultiDict()

        for transition in arch.get_architecture_transitions():
            if (isinstance(transition.guard, BaseAccess.Access)
                    and str(transition.guard) in BaseAccess.Access_str_list
                    and not transition.out_msg
                    and not ProtoParserBase.k_cond in [str(operation) for operation in transition.operations]
                    and not ProtoParserBase.k_ncond in [str(operation) for operation in transition.operations]):
                if (transition.start_state not in self.state_permission_map or
                        str(transition.guard) not in self.state_permission_map[transition.start_state]):
                    self.state_permission_map[transition.start_state] = str(transition.guard)

    def gen_state_access_perm(self, transition: Transition_v2) -> str:
        # First reset state permission
        access_perm_str = self.f_clear_perm + "(" + MurphiTokens.v_adr + ", " + MurphiTokens.v_mach + ");"

        # Check if no accesses are defined for state
        if transition.final_state not in self.state_permission_map:
            return access_perm_str + self.nl

        # For access_permission defined in the state set multiset entry
        for access_perm in self.state_permission_map[transition.final_state]:
            access_perm_str += " " + self.f_set_perm + "(" + access_perm + ", " \
                               + MurphiTokens.v_adr + ", " + MurphiTokens.v_mach + ");"

        # If litmus testing enabled call serve access function
        # Check if manual access is defined, if yes then don't replicate access, only single access per transition
        # allowed
        if (self.config.litmus_testing and
                not [op for op in transition.operations
                     if str(op) == ProtoParserBase.k_access
                        and str(op.getChildren()[0]) not in self.arch.event_network.event_issue]):
            access_perm_str += self.gen_serve_cpu_func()

        # If access permission tracking is enabled or litmus testing
        if (self.config.enable_read_write_execution and not self.config.litmus_testing
                and str(transition.guard) == BaseAccess.k_store
                and str(transition.guard) in self.state_permission_map[transition.final_state]):
            access_perm_str += self.gen_serve_access_func()

        return access_perm_str + self.nl

    def gen_tmp_access(self, access: BaseAccess.Access):
        Debug.perror("Access to be executed is not a base access (load/store): " + str(access),
                     str(access) in BaseAccess.Access_str_list)

        # Set the defined access permission and serve CPU if necessary
        access_perm_str = self.f_set_perm + "(" + str(access) + ", " \
                          + MurphiTokens.v_adr + ", " + MurphiTokens.v_mach + ");"

        # If litmus testing enabled call serve access function
        if self.config.litmus_testing:
            access_perm_str += self.gen_serve_cpu_func()

        # At the end of a transition the access clear function is called in self.gen_state_access_perm so any temporary
        # access permissions will be cleared

        return access_perm_str

    def gen_remote_event_serve(self, remote_event: str):
        Debug.perror("Expected event, but passed object has different type: " + str(remote_event),
                     str(remote_event) in self.arch.event_network.event_issue)

        return self._stringReplKeys(self._openTemplate(MurphiTemplates.f_remote_event_serve_func),
                                    [
                                        str(remote_event),
                                        str(self.arch)
                                        ])

    def gen_serve_cpu_func(self):
        return (self.nl + self.f_exe_cpu_access + "(" + MurphiTokens.v_cbe + "." + self.get_data_variable() + ", " +
                MurphiTokens.v_adr + ", " + MurphiTokens.v_mach + ");")

    def gen_serve_access_func(self):
        return (self.nl + self.f_exe_store + "(" + MurphiTokens.v_cbe + "." + self.get_data_variable() + ", " +
                MurphiTokens.v_adr + ");")

    def get_data_variable(self) -> str:
        data_var_list = []
        # Identify data variable
        for variable in self.arch.machine.variables:
            if str(self.arch.machine.variables[variable]) == ProtoParserBase.t_data:
                data_var_list.append(variable)

        Debug.perror("No data variable detected", len(data_var_list))
        Debug.pwarning("Multiple variables data variables detected: " + str(data_var_list), len(data_var_list) > 1)
        return data_var_list[0]
