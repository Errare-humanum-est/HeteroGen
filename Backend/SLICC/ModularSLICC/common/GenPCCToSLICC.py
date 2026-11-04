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

from typing import Dict, Union, Tuple, List
from collections import OrderedDict

from antlr3.tree import CommonTree

from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from Parser.ProtoCCcomTreeFct import toStringList, childsToStringList

from DataObjects.ClassCluster import Cluster
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture

from Debug.Monitor.ClassDebug import Debug

from Backend.SLICC.ModularSLICC import SLICCTokens
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from Backend.SLICC.ModularSLICC.common import Util


class GenPCCToSLICC(TemplateHandler, Debug):
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

    def __init__(self, cluster: Cluster, arch: FlatArchitecture, out_ports: 'OrderedDict[str, str]'):
        Debug.__init__(self)

        self.cluster = cluster
        self.arch = arch
        self.local_variables: Dict[str, str] = {}
        self.out_ports = out_ports

        self.constructed_messages = {}
        self.out_direction = "From" if self.arch.machine.check_dir() else "To"

        # These variables do need to be reset for every new transition
        self.cur_guard_str: str = ""


    def new_transition(self, guard: str):
        self.cur_guard_str = guard

    def gen_operation(self, operation: CommonTree) -> Union[str, None]:

        op = str(operation)

        if op == ProtoParserBase.k_assign:
            # TODO: Gen architecture assignment
            return self.gen_assignment(operation)

        elif op == ProtoParserBase.k_setfunc:
            return self.gen_set_function(operation) + self.end

        ## Condition handling
        elif op == ProtoParserBase.k_cond:
            cond = self.gen_condition(False, operation)
            return f"{SLICCTokens.k_if} ({cond}) {{{self.nl}"

        elif op == ProtoParserBase.k_ncond:
            cond = self.gen_condition(True, operation)
            return f"{SLICCTokens.k_if} ({cond}) {{{self.nl}"

        elif op == ProtoParserBase.k_cond_end:
            return ""
            #return self.gen_condition_end()

        elif op == ProtoParserBase.k_send:
            net, message_var = childsToStringList(operation)
            assert message_var in self.constructed_messages, f"tried to send {message_var} which does not exist"
            message_dict = self.constructed_messages[message_var]
            net = f"{net}{self.out_direction}"

            body = f"out_msg.LineAddress := LineAddress{self.end}" \
                   f"out_msg.MessageSize := {Util.get_message_size(message_dict, self.cluster)}{self.end}" \
                   f"out_msg.Destination.add({message_dict.pop('Destination')}){self.end}"
            for field, val in message_dict.items():
                body += f"out_msg.{field} := {val}{self.end}"
            body = self.add_tabs(body, 1)
            return f"enqueue({self.out_ports[net]}, CoherenceMessage, responseLatency) " \
                   f"{{{self.nl}{body}{self.nl}}}{self.nl}"

        elif op == ProtoParserBase.k_mcast:
            assert self.arch.machine.check_dir(), "TODO only dirs allowed to mcast for now"
            net, message_var, destination_set = childsToStringList(operation)
            assert message_var in self.constructed_messages, f"tried to send {message_var} which does not exist"
            message_dict = self.constructed_messages[message_var]
            net = f"{net}{self.out_direction}"
            body = f"out_msg.LineAddress := LineAddress{self.end}" \
                   f"out_msg.MessageSize := {Util.get_message_size(message_dict, self.cluster)}{self.end}" \
                   f"out_msg.Destination := getEntry(LineAddress).{destination_set}{self.end}"
            message_dict.pop("Destination")  # Destination field overwritten by multicasting
            for field, val in message_dict.items():
                body += f"out_msg.{field} := {val}{self.end}"
            body = self.add_tabs(body, 1)
            return f"enqueue({self.out_ports[net]}, CoherenceMessage, responseLatency) " \
                   f"{{{self.nl}{body}{self.nl}}}{self.nl}"

        elif op == ProtoParserBase.k_bcast:
            raise NotImplementedError

        elif op == ProtoParserBase.k_break:
            return ""

    def gen_assignment(self, operation: CommonTree) -> Union[str, None]:
        tokens = operation.getChildren()
        var_name = tokens[0].getText()
        if var_name == ProtoParserBase.k_state:
            # State should be updated by setState, not hard-coded like this
            return None
        elif tokens[-1].getText() == SLICCTokens.t_MSGCSTR:
            # SLICC seems to not support manually constructing messages, you have to rely
            # purely on the in_msg and out_msg variables given by peek() and enqueue(), respectively.
            # To get around this, we will constructing a message internally and then use this to populate
            # the out_msg upon hitting a send or broadcast operation
            message_entries = tokens[-1].getChildren()
            message_dict = {'Type': f"CoherenceMessageType:{message_entries[1].getText()}",
                            'Sender': self._msg_src_dest(message_entries[2]),
                            'Destination': self._msg_src_dest(message_entries[3])
                            }
            matched_msg_node_vars = None
            for msg_name, msg_type in self.arch.global_arch.network.msg_types.items():
                if msg_name == message_entries[0].getText():
                    matched_msg_node_vars = list(msg_type.msg_vars.keys())
            assert matched_msg_node_vars is not None
            for idx, entry in enumerate(message_entries[4:]):
                message_dict[matched_msg_node_vars[idx]] = self.gen_right_assignment(entry)[0]

            self.constructed_messages[var_name] = message_dict
            return None
        elif var_name in self.arch.machine.variables:
            return Util.get_entry_variable(self.arch, var_name, self._exist_var_assignment(var_name, operation))
        elif var_name in self.local_variables:
            # Variable is local (in the scope)
            return self._exist_var_assignment(var_name, operation)
        else:
            # Create new local variable, keep track of type for future type checking
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
                #self.p_error("Variable: " + var_name + " is used for different data types: " +
                #            str(data_type) + " | " + str(rev_var_type) + "this is not supported by Murphi",
                #            str(data_type) == str(rev_var_type))

        return var_name + " := " + assign_str + self.end

    def gen_right_assignment(self, operation: CommonTree) -> Tuple[str, Union[str, CommonTree, None]]:
        right_assignment = str(operation)

        # Generate message assignment
        if right_assignment == ProtoParserBase.k_msg:
            assert 0, "Message should already have been constructed by parent fn call"

        # Assign integer
        elif right_assignment.isdigit():
            return right_assignment, ProtoParserBase.t_int

        # Variable reassignments
        elif right_assignment in self.arch.machine.variables:
            return Util.get_entry_variable(self.arch, right_assignment, right_assignment), \
                   self.arch.machine.variables[right_assignment]
        elif right_assignment in self.local_variables:
            return right_assignment, self.local_variables[right_assignment]

        # Assignment from Guard or Data Type
        elif right_assignment == self.cur_guard_str:
            # The current guard is an in msg
            if right_assignment in self.arch.global_arch.network.base_message_dict:
                return self._in_msg_assignment(right_assignment, operation)
            # The current guard in an event
            else:
                self.p_error("EVENTS NOT IMPLEMENTED YET")

        elif right_assignment == ProtoParserBase.k_setfunc:
            return self.gen_set_function(operation), None
        elif right_assignment == ProtoParserBase.k_id:
            return SLICCTokens.k_mach, None
        else:
            return "".join(toStringList(operation)), None

    def _msg_src_dest(self, operation: CommonTree) -> str:
        if str(operation) in self.arch.global_arch.network.base_message_dict:
            field = ''.join(childsToStringList(operation))
            field = SLICCTokens.field_map.get(field, field)
            return f"{SLICCTokens.k_in_msg}{field}"
        elif str(operation) in self.arch.machine.variables:
            return Util.get_entry_variable(self.arch, str(operation), str(operation))
        elif str(operation) in self.local_variables:
            assert 0, "NOT Implemented yet"
            return str(operation) + "".join(childsToStringList(operation))
        elif (str(operation) in [str(arch) for arch in self.cluster.get_machine_architectures()]
              and not str(operation) == str(self.arch)):
            if str(operation) in [str(arch) for arch in self.cluster.get_machine_architectures() if arch.machine.check_dir()]:
                # Need to translate directory to use SLICC's directory-mapping function
                return "mapAddressToMachine(LineAddress, MachineType:Directory)"
            return str(operation)
        else:
            return SLICCTokens.k_mach

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
                    base_msg_defs = SLICCTokens.base_message_vars
                    if obj_var in base_msg_defs:
                        var_type = str(base_msg_defs[obj_var])
                        break

            field = ''.join(childsToStringList(operation))
            field = SLICCTokens.field_map.get(field, field)
            return f"{SLICCTokens.k_in_msg}{field}", var_type

        # No children exist so the assignment is the entire message object
        else:
            # TODO don't think this is supported by SLICC, will have to see when it pops up
            return SLICCTokens.k_in_msg, ProtoParserBase.t_msg

    def gen_condition(self, negated: bool, operation: CommonTree) -> str:
        cond_str = ""
        cond_ops = operation.getChildren()
        force_negation = negated
        for op in cond_ops:
            op_str = op.getText()
            if op_str == SLICCTokens.t_SETFUNC:
                cond_str += self.gen_set_function(op)
            elif (op_str, negated) in SLICCTokens.op_map:
                force_negation = False
                cond_str += f" {SLICCTokens.op_map[(op_str, negated)]} "
            else:
                cond_str += self.gen_right_assignment(op)[0]
        if force_negation:
            # SLICC doesn't allow negation with !, so negating some complex expressions
            # (e.g. set functions) requires the below hack, i.e. checking for equality with false
            cond_str += " == false"
        return cond_str

    def gen_condition_end(self) -> str:
        return "}" + self.nl

    @staticmethod
    def gen_final_state(temp_h: TemplateHandler, state: str, arch: FlatArchitecture) -> str:

        if arch.machine.check_cache():
            return f"setState(tbe, getEntry(LineAddress), LineAddress, State:{state})" \
                   f"{temp_h.end}"
        else:
            assert arch.machine.check_dir(), f"Arch {arch} was not level.cache or level.directory"
            return f"setState(tbe, LineAddress, State:{state}){temp_h.end}"

    @staticmethod
    def gen_pop_net(temp_h: TemplateHandler, port_name: str) -> str:
        return f"{port_name}.dequeue(clockEdge()){temp_h.end}"

    ### Vector set functions
    def gen_set_function(self, operation: CommonTree) -> str:
        # TODO check if this really works
        set_ops = operation.getChildren()
        # TODO is the form of a set function always <the set>.<the fn>(<param>)
        target_set = self.gen_right_assignment(set_ops[0])[0]
        set_fn = str(set_ops[2])
        param = self.gen_right_assignment(set_ops[4])[0]

        method_fct = SLICCTokens.set_func_map[set_fn]
        method = getattr(self, method_fct, lambda: '_pass_node')
        return method(target_set, param)

    @staticmethod
    def _gen_vector_add(*args: List[str]) -> str:
        return f"{args[0]}.add({args[1]})"

    @staticmethod
    def _gen_vector_delete(*args: List[str]) -> str:
        return f"{args[0]}.remove({args[1]})"

    @staticmethod
    def _gen_vector_clear(*args: List[str]) -> str:
        return f"{args[0]}.clear()"

    @staticmethod
    def _gen_vector_contains(*args: List[str]) -> str:
        return f"{args[0]}.isElement({args[1]})"

    @staticmethod
    def _gen_vector_empty(*args: List[str]) -> str:
        return f"{args[0]}.count() == 0"

    @staticmethod
    def _gen_vector_count(*args: List[str]) -> str:
        return f"{args[0]}.count()"
