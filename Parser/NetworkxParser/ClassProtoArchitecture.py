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

import copy

from antlr3.tree import CommonTree

from typing import List, Set, Dict

from Debug.Monitor.ClassDebug import Debug

from Parser.NetworkxParser.ClassProtoProcess import ProtoProcess
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.FlowDataTypes.ClassEvent import Event
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from Parser.DataTypes.ClassProtoMachine import ProtoMachine
from Algorithms.ModelChecker.GraphCheck import GraphCheck
from Parser.DataTypes.ClassGuard import Guard

from DataObjects.Architecture.ClassGlobalBaseArchitecture import GlobalBaseArchitecture
from DataObjects.Architecture.ClassBaseArchitecture import BaseArchitecture


## SSPArchitecture
#
#  Parser architecture format containing transition list, ProtoMachine definition including all variables and constants
#  as well as list of all the events and the network node
#  Dependency: ProtoParserBase, Debug
class SSPArchitecture(BaseArchitecture, Debug):

    ArchEntity = {
        'MACHN_': '_check_machine',
        'PROC_': '_create_proc',
        'STABLE_': '_create_stable_state_list',
    }

    def __init__(self, arch_node: CommonTree,
                 machine: ProtoMachine,
                 global_arch: GlobalBaseArchitecture,
                 dbg_graph: bool = False):
        Debug.__init__(self)
        self.dbg_graph: bool = dbg_graph

        self.arch_base_node: CommonTree = arch_node

        BaseArchitecture.__init__(self)

        self.machine: ProtoMachine = machine
        self.global_arch = global_arch

        # Convert these later into proper data objects
        self.stable_state_dict: Dict[str, State_v2] = {}
        self.state_dict: Dict[str, State_v2] = {}

        # Record all ssp_transitions
        self.ssp_transitions: List[Transition_v2] = []
        self.process_tree_list = []

        self._gen_arch(self.arch_base_node)

        # After creating the ssp_transitions, merge all SSPStates with same identifiers into same State
        self._gen_states()
        # After merging the states replace guard place holders that are messages or events with the appropriate objects
        self._update_guards()

        # Register accesses that were used in the SSP, later perform a check that every of these accesses was defined
        # for every stable state
        self.access_types: Set = set()
        self.evict_types: Set = set()

        # Verify if for every state accesses, evicts and events are defined
        self.ssp_input_sanity_checks()

        self.arch_name = self.machine.mach_id
        self.init_state = self.stable_state_dict[self.machine.init_state]
        self.gen_tree_from_trans(set(self.stable_state_dict.values()), set(self.ssp_transitions))

        # GraphCheck needs no return parameter, an error will be thrown if for example terminal state exists
        GraphCheck(self.ssp_transitions)

    def __str__(self):
        return str(self.machine)

    def _gen_arch(self, arch_tree: CommonTree):
        for arch_node in arch_tree.getChildren():
            method_fct = self.ArchEntity[str(arch_node)]
            method = getattr(self, method_fct, lambda: '__UnknownNode__')
            method(arch_node)

    def _check_machine(self, arch_node: CommonTree):
        self.perror("Multiple machine definitions found in tree", str(arch_node.getChildren()[0]) == str(self.machine))

    def _create_stable_state_list(self, stable_state_node: CommonTree):
        self.perror("Multiple stable state definitions found in tree", not self.stable_state_dict)
        if str(stable_state_node) == ProtoParserBase.k_stable:
            for stable_state in stable_state_node.getChildren():
                stable_state = self._gen_state(str(stable_state))
                stable_state.stable = True
                self.stable_state_dict[str(stable_state)] = self._gen_state(str(stable_state))

    def _create_proc(self, process_node: CommonTree):
        process_tree = ProtoProcess(process_node, self.global_arch.base_access, self.global_arch.network,
                                    self.machine.event_network, self.dbg_graph)
        self.process_tree_list.append(process_tree)
        self.ssp_transitions += process_tree.transitions

    def _gen_states(self):
        for transition in self.ssp_transitions:
            new_start_state = self._gen_state(str(transition.start_state))
            transition.replace_start_state(new_start_state)
            new_final_state = self._gen_state(str(transition.final_state))
            transition.replace_final_state(new_final_state)

    def _gen_state(self, state_str: str) -> State_v2:
        if state_str in self.stable_state_dict:
            return self.stable_state_dict[state_str]
        elif state_str in self.state_dict:
            return self.state_dict[state_str]
        else:
            new_state = State_v2(state_str)
            self.state_dict[state_str] = new_state
            return new_state

    def _update_guards(self):
        for transition in self.ssp_transitions:
            if not isinstance(transition.guard, Guard):
                continue
            # Update internal event guards
            if str(transition.guard) in self.machine.event_network.event_issue:
                transition.guard = self.machine.event_network.event_issue[str(transition.guard)]

    ## All functions below check the input SSP specification for completeness and several correctness conditions
    #  @param self The object pointer.
    def ssp_input_sanity_checks(self):
        self.find_access_evict_types()
        # Check if for every stable state all accesses are defined
        self.check_access(self.access_types)
        # Check if for every stable state evicts are defined
        self.check_access(self.evict_types)
        # Check if for every stable state all possible events are defined
        self.check_events()

    # Determine all access types used in the SSP
    def find_access_evict_types(self):
        for transition in self.ssp_transitions:
            if isinstance(transition.guard, BaseAccess.Access):
                self.access_types.add(str(transition.guard))
            elif isinstance(transition.guard, BaseAccess.Evict):
                self.evict_types.add(str(transition.guard))

    # For every stable state all possible accesses used in the SSP must be defined
    def check_access(self, type_set: Set):
        state_access_dict: Dict[str, Set[str]] = {}
        for stable_state in self.stable_state_dict:
            state_access_dict[str(stable_state)] = copy.copy(type_set)

        for transition in self.ssp_transitions:
            if str(transition.start_state) not in state_access_dict:
                continue
            if str(transition.guard) in state_access_dict[str(transition.start_state)]:
                state_access_dict[str(transition.start_state)].remove(str(transition.guard))
            if not len(state_access_dict[str(transition.start_state)]):
                del state_access_dict[str(transition.start_state)]

        if len(state_access_dict) == 1:
            if (list(state_access_dict.keys())[0] == self.machine.init_state and
                    state_access_dict[self.machine.init_state].issubset(set(BaseAccess.Evict_str_list))):
                return

        self.perror("Not all possible accesses/evicts were defined for every stable state: " +
                    str(state_access_dict) + " ,Maybe also check source code architecture brackets",
                    not len(state_access_dict))

    # For every stable state the event behaviour must have been defined, because an event can occur in any stable state
    # like e.g. load, store, evict
    # Also replace the generic guards with the event types
    def check_events(self):
        state_event_dict: Dict[str, Dict[str, Event]] = {}
        for stable_state in self.stable_state_dict:
            state_event_dict[str(stable_state)] = copy.copy(self.machine.event_network.event_issue)

        for transition in self.ssp_transitions:
            if str(transition.start_state) not in state_event_dict:
                continue
            event_dict = state_event_dict[str(transition.start_state)]

            # For each stable state there exists a single transaction guarded byu this event
            if str(transition.guard) in event_dict:
                # Replace guard with event declaration
                transition.guard = event_dict[str(transition.guard)]
                del event_dict[str(transition.guard)]

            if not len(state_event_dict[str(transition.start_state)]):
                del state_event_dict[str(transition.start_state)]

        self.perror("Not all possible events were defined for every stable state: " + str(state_event_dict),
                    not len(state_event_dict))






