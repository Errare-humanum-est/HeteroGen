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

from antlr3.tree import CommonTree

from typing import List, Dict, Union

from Debug.Monitor.ClassDebug import Debug
from Parser.DataTypes.ClassConstants import Constants
from DataObjects.FlowDataTypes.ClassEvent import EventNetwork
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from Algorithms.General.AuxStateHandler import AuxStateHandler


class ProtoMachine:

    k_cache = 'CACHE_'
    k_dir = 'DIR_'
    k_mem = 'MEM_'

    # Later inherit data types
    def __init__(self,
                 arch_node: CommonTree,
                 constants: Constants):

        # Type of the architecture(k_cache, k_dir, k_mem)
        self.mach_type: str = str(arch_node)
        # Name of the architecture
        self.mach_id: str = str(arch_node.getChildren()[0])

        self.constants = constants

        self.init_state: str = None

        # If a set is defined, more machines exist in the system
        self.machine_cnt_const_id: Union[str, None] = None

        self.variables: Dict[str, CommonTree] = {}
        self.variables_init_val: Dict[str, CommonTree] = {}

        self.get_variables(arch_node.getChildren()[1:])

        self.event_network: EventNetwork = EventNetwork()

        Debug.perror("Init state not defined", self.init_state)

    def __str__(self):
        return self.mach_id

    # Extract init state
    def get_variables(self, var_obj_list: List[CommonTree]):
        for var_obj in var_obj_list:
            method_fct = ProtoParserBase.f_objects[var_obj.getText()]
            method = getattr(self, method_fct, lambda: '__UnknownNode__')
            method(var_obj)

    def _init_state(self, init_obj: CommonTree):
        Debug.perror("Multiple init state definitions found", not self.init_state)
        self.init_state = str(init_obj.getChildren()[0])

    def _obj_set_func(self, obj_set_obj: CommonTree):
        # Get constant value if defined
        if str(obj_set_obj.getChildren()[0]) in self.constants.const_dict:
            self.machine_cnt_const_id = str(obj_set_obj.getChildren()[0])
        else:
            Debug.perror("Set count for machine defined, but not number of set constant")

    def _data_func(self, data_obj: CommonTree):
        self.variables[str(data_obj.getChildren()[0])] = data_obj

    def _int_func(self, int_obj: CommonTree):
        self._get_variable(int_obj)

    def _bool_func(self, bool_obj: CommonTree):
        self._get_variable(bool_obj)

    def _id_func(self, id_obj: CommonTree):
        self._get_variable(id_obj)

    def _get_variable(self, var_obj: CommonTree):
        var_obj_var: List[CommonTree] = var_obj.getChildren()
        self.variables[str(var_obj_var[0])] = var_obj
        self._find_init_val(str(var_obj_var[0]), var_obj)

    def _find_init_val(self, var_name: str, obj_def: CommonTree):
        init_val = self._find_token_key(obj_def, ProtoParserBase.k_init_val)
        if init_val:
            self.variables_init_val[var_name] = init_val

    @staticmethod
    def _find_token_key(obj_def: CommonTree, key: str) -> Union[CommonTree, None]:
        for child in obj_def.getChildren():
            if str(child) == key:
                return child
        return None

    # Determine machine type
    def check_cache(self) -> bool:
        if self.mach_type == self.k_cache:
            return True
        return False

    def check_dir(self) -> bool:
        if self.mach_type == self.k_dir:
            return True
        return False

    def check_mem(self) -> bool:
        if self.mach_type == self.k_mem:
            return True
        return False

    ####################################################################################################################
    ### Merge the system descriptors
    ####################################################################################################################

    def update_variable_names(self, new_sub_id: str) -> List[str]:
        variable_keys = list(self.variables.keys())
        ret_variable_keys = []
        for variable in variable_keys:
            # Do not rename the cache line
            if str(self.variables[variable]) == ProtoParserBase.k_data:
                continue
            ret_variable_keys.append(variable)

            # Update dict entry
            self.variables[variable + new_sub_id] = AuxStateHandler.cond_rename_operation(self.variables[variable],
                                                                                          variable,
                                                                                          variable + new_sub_id,
                                                                                          [])
            # Clear old dict entry
            self.variables.pop(variable)

            # Update init variable names
            if variable in self.variables_init_val:
                self.variables_init_val[variable + new_sub_id] = self.variables_init_val[variable]
                self.variables_init_val.pop(variable)

        return ret_variable_keys

    def update_mach_cnt_constant_name(self, new_sub_id: str):
        if self.machine_cnt_const_id:
            self.machine_cnt_const_id += new_sub_id

    def modify_variable_names(self, cur_const: str, new_const: str):
        for var_key in self.variables:
            self.variables[var_key] = \
                AuxStateHandler.cond_rename_operation(self.variables[var_key], cur_const, new_const)

        for var_key in self.variables_init_val:
            self.variables_init_val[var_key] = \
                AuxStateHandler.cond_rename_operation(self.variables_init_val[var_key], cur_const, new_const)

    ####################################################################################################################
    ### Merge ProtoMachines
    ####################################################################################################################
    def merge_machine(self, other: 'ProtoMachine'):
            self.variables.update(other.variables)
            self.variables_init_val.update(other.variables_init_val)

            self.event_network.merge_event_networks(other.event_network)

