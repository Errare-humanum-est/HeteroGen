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

# Instead of having everything in the parser gen_make for every architecture a single object that contains all
# important information

from typing import Set, Dict

from Debug.Graphv.ProtoCCGraph import ProtoCCGraph

from Algorithms.ControllerGeneration.NetworkxGeneral.TraceNetworkx import TreeNetworkx
from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.FlowDataTypes.ClassEvent import EventNetwork
from Parser.DataTypes.ClassProtoMachine import ProtoMachine
from DataObjects.Architecture.ClassGlobalBaseArchitecture import GlobalBaseArchitecture
from DataObjects.FlowDataTypes.ClassBaseAccess import Access

## Documentation for a function.
#
#  More details.
class BaseArchitecture(TreeNetworkx):
    def __init__(self, gdbg: bool = False):
        self.gdbg = gdbg

        # Generates the graph tree
        TreeNetworkx.__init__(self, False)

        self.arch_name = None
        self.init_state = None

        self.machine: ProtoMachine = None
        self.global_arch: GlobalBaseArchitecture = None
        self.event_network: EventNetwork = None

    def __str__(self):
        return self.arch_name

    # OUTPUT FUNCTIONS
    def draw_controller(self):
        ProtoCCGraph("Spec: " + self.arch_name, list(self.get_architecture_transitions()))

    def copy_base_architecture(self, other: 'BaseArchitecture'):
        self.arch_name = other.arch_name
        self.machine = other.machine
        self.event_network = self.machine.event_network
        self.global_arch = other.global_arch
        self.init_state = other.init_state

        # TreeNetworkx
        self.stable_states = other.stable_states
        self.state_sub_tree_dict = other.state_sub_tree_dict

    def copy_base_architecture_constants(self, other: 'BaseArchitecture'):
        self.arch_name = other.arch_name
        self.machine = other.machine
        self.event_network = self.machine.event_network
        self.global_arch = other.global_arch

    def update_base_fsm(self, init_state: State_v2, stable_states: Set[State_v2], transitions: Set[Transition_v2]):
        self.init_state = init_state
        self.gen_tree_from_trans(stable_states, transitions)

    ####################################################################################################################
    # Renaming functions
    ####################################################################################################################
    def update_var_and_func(self, new_sub_id: str):
        # Update machine name
        self.arch_name += new_sub_id
        # Update variable names in the machine definition
        self.update_variable_names(new_sub_id)
        # Update event functions
        self.update_event_names(new_sub_id)
        # Update the machine cnt constant
        self.machine.update_mach_cnt_constant_name(new_sub_id)

    def update_arch_name(self, new_sub_id: str):
        self.arch_name += new_sub_id

    def update_variable_names(self, new_sub_id: str):
        # Update variables in machine container and then change names of all modified variables in transition operations
        for variable_name in self.machine.update_variable_names(new_sub_id):
            self.replace_transitions_objects(variable_name, variable_name + new_sub_id)

    def update_event_names(self, new_sub_id: str):
        # For the event like for the message constructor the send function names must be updated!
        for event in self.event_network.event_issue:
            self.replace_transitions_objects(event, event + new_sub_id)

    def update_dict_names(self, old_to_new_identifier_dict: Dict[str, str]):
        for old_identifier in old_to_new_identifier_dict:
            self.replace_transitions_objects(old_identifier, old_to_new_identifier_dict[old_identifier])

    def replace_transitions_objects(self, var_name: str, new_var_name: str):
        for transition in self.get_architecture_transitions():
            transition.rename_operation(var_name, new_var_name)

