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

from typing import Dict, Union, Tuple
from antlr3.tree import CommonTree

from Backend.Murphi.MurphiModular.General import GenPCCToMurphi
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from Parser.ProtoCCcomTreeFct import toStringList, childsToStringList

from DataObjects.ClassCluster import Cluster
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture

from Debug.Monitor.ClassDebug import Debug

from Backend.Murphi.MurphiModular.General.GenDataTypes import GenDataTypes
from Backend.Murphi.MurphiModular.General.BaseMessageTypes import BaseMessageTypes
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Backend.Murphi.BaseConfig import BaseConfig
from Backend.Murphi.MurphiModular.StateMachines.GenMurphiAccess import GenMurphiAccess
from Backend.Murphi.MurphiModular.General.GenDataTypes import GenDataTypes
#from Backend.Murphi.MurphiModular.General.GenPCCToMurphi import GenPCCToMurphi


class GenPCCtoMurphi_Rev(GenDataTypes, GenMurphiAccess, Debug):
    set_func = {
        "add": "_mod_element",
        "del": "_mod_element",
        "clear": "_clear_vector",
        "contains": "_mod_element",
        "empty": "_mod_element",
        "count": "_vector_count"
    }

    set_func_str = {
        "add": "AddElement_",
        "del": "RemoveElement_",
        "clear": "ClearVector_",
        "contains": "IsElement_",
        "empty": "HasElement_",
        "count": "VectorCount_"
    }

    def __init__(self, cluster: Cluster, arch: FlatArchitecture, config: BaseConfig):
        GenDataTypes.__init__(self, str(arch))
        GenMurphiAccess.__init__(self, arch, config)
        Debug.__init__(self)

        self.cluster = cluster
        self.arch = arch
        self.local_variables: Dict[str, str] = {}
        self.config = config

        # These variables do need to be reset for every new transition
        self.cur_guard_str: str = ""

    def new_transition(self, guard: str):
        self.cur_guard_str = guard

    def gen_operation(self, operation: CommonTree) -> Union[str, None]:

        op = str(operation)

        if op == ProtoParserBase.k_assign:
            return self.gen_assignment(operation)

        elif op == ProtoParserBase.k_setfunc:
            return self.gen_set_function(operation) + self.end

        ## Condition handling
        elif op == ProtoParserBase.k_cond:
            return MurphiTokens.k_if + " (" + self.gen_condition(operation) + ") " + MurphiTokens.k_then + self.nl

        elif op == ProtoParserBase.k_ncond:
            return MurphiTokens.k_if + " !(" + self.gen_condition(operation) + ") " + MurphiTokens.k_then + self.nl

        elif op == ProtoParserBase.k_cond_end:
            return ""
            # return self.gen_condition_end()

        ## Send functions
        elif op == ProtoParserBase.k_send:
            # At the send function test if variable is either defined in variables or is defined as a local variable
            return self.gen_send_function(operation)

        elif op == ProtoParserBase.k_mcast:
            return self.gen_multicast_function(operation)

        elif op == ProtoParserBase.k_bcast:
            return self.gen_broadcast_function(operation)

        elif op == ProtoParserBase.k_event:
            return self.gen_event_call(operation)

        elif op == ProtoParserBase.k_access:
            return self.gen_access_func(operation)

        elif op == ProtoParserBase.k_break:
            return ""

        elif op == ProtoParserBase.k_undef:
            return self.gen_undef_var(operation)

        elif op == ProtoParserBase.k_endproc or op == ProtoParserBase.k_endwhen:
            return None

        else:
            print("Unknown operation: " + str(op))
            return self.gen_remote_event_serve(op)
            return None

    def gen_assignment(self, operation: CommonTree) -> Union[str, None]:
        tokens = operation.getChildren()
        var_name = str(tokens[0])

        self.perror("Assignment to short", len(tokens) != 2)

        if var_name == ProtoParserBase.k_state:
            # The next state assignment happens at the end of the transition automatically
            return None

        # The variable has been defined before
        elif var_name in self.arch.machine.variables:
            # Add object prefix for variable access
            return MurphiTokens.v_cbe + "." + self._exist_var_assignment(var_name, operation)

        elif var_name in self.local_variables:
            return self._exist_var_assignment(var_name, operation)
        else:
            # create new local variable
            # Type check right hand side of the assignment
            assign_str, data_type = self.gen_right_assignment(operation.getChildren()[2])
            self.local_variables[var_name] = data_type
            return var_name + " := " + assign_str + self.end

    def _exist_var_assignment(self, var_name: str, operation: CommonTree):
        assign_str = ""

        for child_operation in operation.getChildren()[2:]:
            new_assign_str, data_type = self.gen_right_assignment(child_operation)
            assign_str += new_assign_str
            if data_type:
                if var_name in self.arch.machine.variables:
                    rev_var_type = self.arch.machine.variables[var_name]
                else:
                    rev_var_type = str(self.local_variables[var_name])

                # Do type checking to check if variable is assigned different values breaking Murphi
                #self.perror("Variable: " + var_name + " is used for different data types: " +
                #            str(data_type) + " | " + str(rev_var_type) + "this is not supported by Murphi",
                #            str(data_type) == str(rev_var_type))

        return var_name + " := " + assign_str + self.end

    def gen_right_assignment(self, operation: CommonTree) -> Tuple[str, Union[str, CommonTree, None]]:
        right_assignment = str(operation)

        # Generate message assignment
        if right_assignment == ProtoParserBase.k_msg:
            return self.gen_msg_function(operation), ProtoParserBase.t_msg

        # Assign integer
        elif right_assignment.isdigit():
            return right_assignment, ProtoParserBase.t_int

        # Variable reassignments
        elif right_assignment in self.arch.machine.variables:
            return MurphiTokens.v_cbe + "." + right_assignment + "".join(childsToStringList(operation)), \
                   self.arch.machine.variables[right_assignment]
        elif right_assignment in self.local_variables:
            if self.local_variables[right_assignment] == ProtoParserBase.t_msg:
                return right_assignment + "." + str(operation.getChildren()[1]), self.local_variables[right_assignment]
            else:
                return right_assignment, self.local_variables[right_assignment]

        # Assignment from Guard or Data Type
        elif right_assignment == self.cur_guard_str:
            # The current guard is an in msg
            if right_assignment in self.arch.global_arch.network.base_message_dict:
                return self._in_msg_assignment(right_assignment, operation)
            # The current guard in an event
            else:
                self.perror("EVENTS CARRYING DATA NOT IMPLEMENTED YET")

        elif right_assignment == ProtoParserBase.k_setfunc:
            return self.gen_set_function(operation), None
        elif right_assignment == ProtoParserBase.k_id:
            return MurphiTokens.v_mach, None
        else:
            return "".join(toStringList(operation)), None

    def gen_msg_function(self, msg_object: CommonTree) -> str:
        definition = msg_object.getChildren()
        msg_obj = definition[0].getText()

        msg_type = str(definition[1])

        self.perror("Murphi backend encountered unknown message type",
                    msg_type in self.arch.global_arch.network.base_message_dict)

        msg_src = self._msg_src_dest(definition[2])
        msg_dest = self._msg_src_dest(definition[3])

        # Request(adr: Address; mtype: MessageType; src: Machines; dst: Machines;

        conststr = msg_obj + "("
        # Address
        conststr += MurphiTokens.v_adr + ","
        # Messagetype
        conststr += msg_type + ","
        conststr += msg_src + ","
        conststr += msg_dest

        if len(definition) > 4:
            for ind in range(4, len(definition)):
                conststr += "," + self.gen_right_assignment(definition[ind])[0]
        conststr += ")"

        return conststr

    def _msg_src_dest(self, operation: CommonTree) -> str:
        if str(operation) in self.arch.global_arch.network.base_message_dict:
            return MurphiTokens.v_in_msg + "".join(childsToStringList(operation))
        elif str(operation) in self.arch.machine.variables:
            return MurphiTokens.v_cbe + "." + str(operation) + "".join(childsToStringList(operation))
            #return MurphiTokens.v_cbe + "." + str(operation)
        elif str(operation) in self.local_variables:
            return str(operation) + "".join(childsToStringList(operation))
        elif (str(operation) in [str(arch) for arch in self.cluster.get_machine_architectures()]
              and not str(operation) == str(self.arch)):
            return str(operation)
        else:
            return MurphiTokens.v_mach

    def _in_msg_assignment(self, right_assignment: str,
                           operation: CommonTree) -> Tuple[str, Union[str, CommonTree, None]]:
        # A variable within the message object is accessed
        if operation.getChildren():
            obj_var = str(operation.getChildren()[1])
            msg_defs = self.arch.global_arch.network.base_message_dict[right_assignment]

            var_type = None
            for msg_def in msg_defs:
                msg_type = msg_def.msg_type
                # The assignment is related to a standard message type
                if obj_var in msg_type.msg_vars:
                    var_type = str(msg_type.msg_vars[obj_var])
                    break
                else:
                    base_type_defs = BaseMessageTypes().base_type_defs
                    if obj_var in base_type_defs:
                        var_type = str(base_type_defs[obj_var])
                        break

            if not var_type:
                self.pwarning("The variable: " + obj_var + " is not defined for the message type " +
                              str(msg_defs[0].msg_type))
                if obj_var in self.config.super_type_defs:
                    var_type = self.config.super_type_defs[obj_var]
                else:
                    self.perror("Variable accessed by message object has never been defined")

            return MurphiTokens.v_in_msg + "".join(childsToStringList(operation)), var_type

        # No children exist so the assignment is the entire message object
        else:
            return MurphiTokens.v_in_msg, ProtoParserBase.t_msg

    def gen_condition(self, operation: CommonTree) -> str:
        cond_ops = operation.getChildren()

        if len(cond_ops) == 1:
            return self.gen_right_assignment(cond_ops[0])[0]

        elif len(cond_ops) == 3:
            cond_operation = str(cond_ops[1])
            if cond_operation == "==":
                cond_operation = "="

            return (self.gen_right_assignment(cond_ops[0])[0] + " " +
                    cond_operation + " " + self.gen_right_assignment(cond_ops[2])[0])
        else:
            self.perror("Condition assignment unrecognized: " + "".join(childsToStringList(operation)))

    def gen_condition_end(self) -> str:
        return MurphiTokens.k_endif + self.end

    def gen_send_function(self, operation: CommonTree) -> str:
        send_ops = operation.getChildren()
        self.perror("Send has wrong format: " + "".join(childsToStringList(operation)), len(send_ops) == 2)

        self.perror("Unknown virtual channel message assignment: " + str(send_ops[0]),
                    self.arch.global_arch.network.get_virtual_channel(str(send_ops[0])))

        self.perror("Message has not be defined prior to sending: " + str(send_ops[1]),
                    str(send_ops[1]) in self.local_variables or str(send_ops[1]) in self.arch.machine.variables)

        return str(MurphiTokens.k_send_single + str(send_ops[0]) + "(" + str(send_ops[1]) + ", " + MurphiTokens.v_mach
                   + ")" + self.end)

    def gen_multicast_function(self, operation: CommonTree):
        send_ops = operation.getChildren()
        self.perror("Multicast has wrong format: " + "".join(childsToStringList(operation)), len(send_ops) == 3)
        self.perror("Message has not be defined prior to sending: " + str(send_ops[1]),
                    str(send_ops[1]) in self.local_variables or str(send_ops[1]) in self.arch.machine.variables)
        multi_str = ""
        multi_str += MurphiTokens.k_send_multi + str(send_ops[0]) + "_" + MurphiTokens.k_vector + str(send_ops[2])
        multi_str += "(" + str(send_ops[1]) + ", "
        multi_str += self.gen_right_assignment(send_ops[2])[0] + ", " + MurphiTokens.v_mach + ")" + self.end
        return multi_str

    def gen_broadcast_function(self, operation: CommonTree):
        send_ops = operation.getChildren()
        self.perror("Broadcast has wrong format: " + "".join(childsToStringList(operation)), len(send_ops) == 2)
        self.perror("Message has not be defined prior to sending: " + str(send_ops[1]),
                    str(send_ops[1]) in self.local_variables or str(send_ops[1]) in self.arch.machine.variables)
        return MurphiTokens.k_send_broad + str(send_ops[0]) + "_" + str(self.cluster) + "(" + str(send_ops[1]) \
               + ", " + MurphiTokens.v_mach + ")" + self.end

    def gen_event_call(self, operation: CommonTree) -> str:
        event_op = operation.getChildren()
        self.perror("Event issue has wrong format: " + "".join(childsToStringList(operation)), len(event_op) == 1)
        return MurphiTokens.k_issue_event + str(self.arch) + "(" + str(self.arch) + "_" + str(event_op[0]) \
               + ", " + MurphiTokens.v_mach + ", " + MurphiTokens.v_adr + ")" + self.end

    def gen_access_func(self, operation: CommonTree) -> str:
        access_op = operation.getChildren()[0]
        # Check if the access is a CPU access or a remote event access
        if access_op in self.arch.event_network.event_issue:
            return self.gen_remote_event_serve(access_op)
        else:
            return self.gen_tmp_access(access_op)

    def gen_final_state(self, state):
        final_state_str = MurphiTokens.v_cbe + "." + ProtoParserBase.k_state + " := " + \
                          str(self.arch) + "_" + str(state) + self.end
        return final_state_str

    ### Vector set functions
    def gen_set_function(self, operation: CommonTree) -> str:
        set_ops = operation.getChildren()

        self.perror("Vector variable not specified: " + str(set_ops[0]) + " ,in architecture: " + str(self.arch),
                    str(set_ops[0]) in self.config.var_vector_map)

        self.perror("Vector operation not defined: " + str(set_ops[2]), str(set_ops[2]) in self.set_func)

        method_fct = self.set_func[str(set_ops[2])]
        method = getattr(self, method_fct, lambda: '__UnknownNode__')
        set_func_str = method(operation)

        return set_func_str

    def _mod_element(self, operation: CommonTree) -> str:
        set_ops = operation.getChildren()
        add_element_str = self._base_element_format(operation)
        add_element_str += ", " + self.gen_right_assignment(set_ops[4])[0]
        add_element_str += ")"

        return add_element_str

    def _clear_vector(self, operation: CommonTree) -> str:
        return self._base_element_format(operation) + ")"

    def _vector_count(self, operation: CommonTree) -> str:
        return self._base_element_format(operation) + ")"

    def _base_element_format(self, operation: CommonTree) -> str:
        set_ops = operation.getChildren()
        add_element_str = self.set_func_str[str(set_ops[2])] + str(set_ops[0]) + "("
        add_element_str += MurphiTokens.v_cbe + "." + str(set_ops[0])
        return add_element_str

    def gen_local_variables(self) -> str:
        var_list_str = ""
        for local_var in self.local_variables:
            var_list_str += MurphiTokens.k_var + " " + local_var + ": " + \
                            self._gen_var_type(local_var) + self.end

        return var_list_str

    def _gen_var_type(self, var_name: str) -> str:
        var_type = self.local_variables[var_name]
        if var_type == ProtoParserBase.t_msg:
            return MurphiTokens.k_message
        elif var_type == ProtoParserBase.t_int:
            self.perror("Murphi cannot handle integers with an unknown range: " + var_name)

        self.perror("Data type not defined in Murphi Backend: " + str(var_type) + " for variable: " + var_name)

    def gen_undef_var(self, operation: CommonTree) -> str:
        tokens = operation.getChildren()
        var_name = str(tokens[0])

        # The variable has been defined before
        if var_name in self.arch.machine.variables:
            # Add object prefix for variable access
            return MurphiTokens.k_undefine + ' ' + MurphiTokens.v_cbe + "." + var_name + self.end

        elif var_name in self.local_variables:
            return MurphiTokens.k_undefine + ' ' + var_name + self.end

