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
from typing import Set

from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess
from Parser.DataTypes.ClassBaseNetwork import BaseNetwork
from Parser.DataTypes.ClassConstants import Constants
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase


## Documentation for a function.
#
#  More details.
class GlobalBaseArchitecture:
    def __init__(self):
        self.base_access: BaseAccess = None
        self.network: BaseNetwork = None
        self.constants: Constants = None
        self.dependent_level_list = []                  # Contains all levels that need to be updated together

    def copy(self, other: 'GlobalBaseArchitecture'):
        # Networks and Events
        # Only instantiated to reduce length of access typing in code...
        self.base_access: BaseAccess = other.base_access
        self.network: BaseNetwork = other.network

    def merge_base_architecture(self, other: 'GlobalBaseArchitecture'):
        self.base_access.merge_base_access(other.base_access)
        self.network.merge_networks(other.network)
        self.constants.merge_constants(other.constants)
        self.dependent_level_list += other.dependent_level_list

    def register_level(self, level):
        self.dependent_level_list.append(level)

    def get_dependent_architectures(self) -> Set['FlatArchitecture']:
        arch_set: Set['FlatArchitecture'] = set()
        for level in self.dependent_level_list:
            for arch in level.get_architectures():
                arch_set.add(arch)
        return arch_set

    ## Variable names and send functions are extended by cluster and level id to distinguish variables when introducing
    # hierarchies
    def update_global_identifiers(self, new_sub_id: str):
        archs = self.get_dependent_architectures()
        arch_str_list = [str(arch) for arch in archs]

        # Update all registered levels
        for arch in archs:
            arch.update_var_and_func(new_sub_id)
            # Update all the other architecture identifiers
            for arch_str in arch_str_list:
                arch.replace_transitions_objects(arch_str, arch_str + new_sub_id)

        # Now update the messages and functions in base and child architectures
        self.update_network_and_message_names(new_sub_id)
        # Now update the constants
        self.update_constants(new_sub_id)
        # Update all events in event network definitions
        self.update_event_networks(new_sub_id)

    # Update message names and message type objects
    def update_network_and_message_names(self, new_sub_id: str):
        # Rename the message names
        # First rename all transition Commontree occurences
        for message_name in self.network.base_message_dict:
            self.replace_transition_objects_in_levels(message_name, message_name + new_sub_id)
        self.network.update_base_message_names(new_sub_id)

        # Rename the message send functions
        for msg_type in self.network.msg_types:
            self.replace_transition_objects_in_levels(msg_type, msg_type + new_sub_id)
            # Update the message variable names in the machine description. The variable names in the messages will be
            # updated itself at a later stage
            for msg_var in self.network.msg_types[msg_type].msg_vars:
                # Do not rename the cache line
                if str(self.network.msg_types[msg_type].msg_vars[msg_var]) == ProtoParserBase.k_data:
                    continue
                self.replace_transition_objects_in_levels(msg_var, msg_var + new_sub_id)
        self.network.update_msg_type_names(new_sub_id)

    def update_constants(self, new_sub_id: str):
        constants = self.constants.update_const_names(new_sub_id)
        # The constants must be updated in the transitions and the message definitions
        for base_const in constants:
            self.replace_transition_objects_in_levels(base_const, base_const + new_sub_id)
            self.network.modify_variable_names(base_const, base_const + new_sub_id)

        # Constants must be updated in machine variables and init values
        for arch in self.get_dependent_architectures():
            for base_const in constants:
                arch.machine.modify_variable_names(base_const, base_const + new_sub_id)

    def update_event_networks(self, new_sub_id: str):
        event_networks = [arch.event_network for arch in self.get_dependent_architectures()]
        event_name_str_set = {event_str: event_str + new_sub_id for event_network in event_networks
                              for event_str in event_network.get_event_names()}
        for event_network in event_networks:
            event_network.update_event_names(event_name_str_set)

    def replace_transition_objects_in_levels(self, var_name: str, new_var_name: str):
        for arch in self.get_dependent_architectures():
            arch.replace_transitions_objects(var_name, new_var_name)
