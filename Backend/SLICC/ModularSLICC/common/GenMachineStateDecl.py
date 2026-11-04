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

from DataObjects.States.ClassStatev2 import State_v2
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from typing import Dict
from Algorithms.HeteroGen.ClassHHDirArchitecture import HHDirArchitecture
from Backend.SLICC.ModularSLICC.common import Util
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess
from DataObjects.States.ClassCompoundState import CompoundState
from Parser.DataTypes.ClassProtoMachine import ProtoMachine


class GenMachineStateDecl:
    k_busy = "busy"
    _state_2_permission_cache: Dict[str, str] = {}

    @staticmethod
    def gen_machine_state_decl_body_str(temp_h: TemplateHandler, arch: FlatArchitecture, cache: bool) -> str:
        state_declarations = []
        for state in sorted(arch.get_architecture_states_verified(), key=lambda s: s.state):
            state_declarations.append(
                temp_h.tab + temp_h.string_repl_keys(
                    temp_h.open_template("state_declaration_entry.sm"),
                    [str(state),
                     GenMachineStateDecl._get_access_permission(arch, cache, state)
                     ]
                )
            )

        return temp_h.nl.join(state_declarations)

    @staticmethod
    def _get_access_permission(arch: FlatArchitecture, cache: bool, state: State_v2) -> str:
        state_to_permission = GenMachineStateDecl._state_2_permission_cache
        # The protocols do not give the directory's permission in a state (the memory controller's
        # requests are not modelled): it is derived from the permissions of the caches.
        if isinstance(arch, HHDirArchitecture):
            assert isinstance(state, CompoundState)
            first_state, second_state = state.base_states
            if (first_state.stable and second_state.stable) or not (first_state.state in state_to_permission) or not (second_state.state in state_to_permission):
                perms = Util.get_compound_perms(arch, state, GenMachineStateDecl.k_busy)
                c, = [p for a, p in perms if a.machine.mach_type == ProtoMachine.k_cache]
                d, = [p for a, p in perms if a.machine.mach_type == ProtoMachine.k_dir]

                if GenMachineStateDecl.k_busy in c or GenMachineStateDecl.k_busy in d:
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Busy"
                    return "Busy"
                elif BaseAccess.k_store in c and not BaseAccess.k_load in d:
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Read_Write"
                    return "Read_Write"
                elif BaseAccess.k_load in c and not BaseAccess.k_store in d:
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Read_Only"
                    return "Read_Only"
                elif len(c) == 0:
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Invalid"
                    return "Invalid"
                else:
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Maybe_Stale"
                    return "Maybe_Stale"
            else:
                if state_to_permission[first_state.state] == "Invalid" and state_to_permission[second_state.state] == "Invalid":
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Invalid"
                    return "Invalid"
                else:
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Read_Only"
                    return "Read_Only"
        elif arch.machine.mach_type == ProtoMachine.k_dir:
            if not state.stable:
                accesses = Util.get_arch_access_perms(arch, state, BaseAccess.k_load)
            else:
                accesses = Util.get_arch_access_perms(arch, state, GenMachineStateDecl.k_busy)


        # This definitely needs to evolve in the future...
        if not cache:
            if GenMachineStateDecl.k_busy in accesses:
                return "Busy"
            elif BaseAccess.k_store in accesses:
                return "Maybe_Stale"
            elif BaseAccess.k_load in accesses:
                return "Read_Only"
            else:
                assert state.stable
                return "Read_Write"
        else:
            accesses = Util.get_arch_access_perms(arch, state, GenMachineStateDecl.k_busy)
            if state.stable:
                if GenMachineStateDecl.k_busy in accesses:
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Busy"
                    return "Busy"
                elif BaseAccess.k_store in accesses:
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Read_Write"
                    return "Read_Write"
                elif BaseAccess.k_load in accesses:
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Read_Only"
                    return "Read_Only"
                else:
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Invalid"
                    return "Invalid"
            elif state.start_state_set:
                stable_state = state.start_state_set[0].stable_state
                accesses_stable_state = Util.get_arch_access_perms(arch, stable_state, GenMachineStateDecl.k_busy)
                if len(accesses_stable_state) == 0:
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Invalid"
                    return "Invalid"
                else:
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Read_Only"
                    return "Read_Only"
            else:
                stable_state = state.end_state_set[0].stable_state
                accesses_stable_state = Util.get_arch_access_perms(arch, stable_state, GenMachineStateDecl.k_busy)
                if len(accesses_stable_state) == 0:
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Invalid"
                    return "Invalid"
                else:
                    GenMachineStateDecl._state_2_permission_cache[state.state] = "Read_Write"
                    return "Read_Only"
