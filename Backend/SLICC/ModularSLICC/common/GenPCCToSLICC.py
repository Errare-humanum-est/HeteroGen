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
from Algorithms.ControllerGeneration.General.DeferMessage.NestedDeferMessage import NestedDeferMessage
from Backend.SLICC.ModularSLICC.BackendOptions import OPTIONS, LLC_BANKED, LLC_RANGE


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

    def __init__(self, cluster: Cluster, arch: FlatArchitecture, cache: bool, out_ports: 'OrderedDict[str, str]', machine_mappings: dict[str, str]):
        Debug.__init__(self)

        self.cluster = cluster
        self.arch = arch
        self.cache = cache
        self.local_variables: Dict[str, str] = {}
        self.out_ports = out_ports
        self.machine_mappings = machine_mappings

        self.constructed_messages = {}
        self.out_direction = "From" if not cache else "To"

        # These variables do need to be reset for every new transition
        self.cur_guard_str: str = ""
        self.proxy_keys = {}
        if isinstance(arch, NestedDeferMessage):
            self.proxy_keys = arch.proxy_keys.values()

    # SLICC types of the message payload fields that may be snapshotted (data blocks are not)
    msg_field_types = {
        ProtoParserBase.t_int: SLICCTokens.st_int,
        ProtoParserBase.t_bool: SLICCTokens.st_bool,
        ProtoParserBase.t_id: SLICCTokens.st_mach_id,
    }

    @staticmethod
    def _reads_mutable_state(value: str) -> bool:
        return "getEntry(" in value or "tbe." in value

    def new_transition(self, guard: str):
        self.cur_guard_str = guard

    def gen_operation(self, operation: CommonTree) -> Union[str, None]:

        op = str(operation)

        if op == ProtoParserBase.k_assign:
            assignments = self.gen_assignment(operation)
            if not assignments:
                return None
            for assignment in assignments.splitlines():
                if ":=" in assignment:
                    l, r = assignment.strip()[:-1].split(":=")
                    if l.strip() == r.strip():
                        return None
                else:
                    continue
            return assignments

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
            Util.drop_unread_data(message_dict, self.arch.global_arch)
            net = f"{net}{self.out_direction}"

            body = f"out_msg.LineAddress := LineAddress{self.end}" \
                   f"out_msg.MessageSize := {Util.get_message_size(message_dict, self.arch.global_arch)}{self.end}" \
                   f"out_msg.Destination.add({message_dict.pop('Destination')}){self.end}"
            for field, val in message_dict.items():
                body += f"out_msg.{field} := {val}{self.end}"
            body = self.add_tabs(body, 1)
            return f"enqueue({self.out_ports[net]}, CoherenceMessage, responseLatency) " \
                   f"{{{self.nl}{body}{self.nl}}}{self.nl}"

        elif op == ProtoParserBase.k_mcast:
            net, message_var, destination_set = childsToStringList(operation)
            assert message_var in self.constructed_messages, f"tried to send {message_var} which does not exist"
            message_dict = self.constructed_messages[message_var]
            Util.drop_unread_data(message_dict, self.arch.global_arch)
            net = f"{net}{self.out_direction}"
            body = f"out_msg.LineAddress := LineAddress{self.end}" \
                   f"out_msg.MessageSize := {Util.get_message_size(message_dict, self.arch.global_arch)}{self.end}" \
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

        elif op == ProtoParserBase.k_access:
            # The bytes of a store of release-consistency code, which the sequencer does not write
            if Util.is_rc_store(self.cur_guard_str) and str(operation.getChildren()[0]) == "store":
                return f"writeRCData(tbe, getEntry(LineAddress), LineAddress, " \
                       f"{SLICCTokens.k_in_msg}.WTData, {SLICCTokens.k_in_msg}.{SLICCTokens.write_mask}){self.end}"
            return None

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
            matched_msg_type = None
            for msg_name, msg_type in self.arch.global_arch.network.msg_types.items():
                if str(msg_type) == message_entries[0].getText():
                    matched_msg_type = msg_type
            assert matched_msg_type is not None
            matched_msg_node_vars = list(matched_msg_type.msg_vars.keys())

            # The payload is evaluated when the message is constructed (PCC semantics). Fields that
            # read mutable controller state (e.g. `cache.count()`) are therefore snapshotted into a
            # local variable here; otherwise the expression would be evaluated where the field is
            # used, possibly after the state changed (e.g. after `cache.clear()`).
            # Not for machines that access main memory: GenMachineInPorts.replace_mem_ops moves the
            # code after a memory access into the memory response handler, where a local declared
            # here would be out of scope. There the whole sub-tree moves together while the
            # directory waits in a transient state, so the deferred evaluation is equivalent.
            snapshot = not Util.must_access_memory(self.cache)
            snapshots = []
            for idx, entry in enumerate(message_entries[4:]):
                field = matched_msg_node_vars[idx]
                value = self.gen_right_assignment(entry)[0]
                slicc_type = self.msg_field_types.get(str(matched_msg_type.msg_vars[field]))
                if snapshot and slicc_type is not None and self._reads_mutable_state(value):
                    local = f"{var_name}_{field}"
                    snapshots.append(f"{slicc_type} {local} := {value}{self.end}")
                    value = local
                message_dict[field] = value

            if message_entries[1].getText() in Util.partial_messages(self.arch.global_arch):
                message_dict[SLICCTokens.write_mask] = self._write_mask(message_entries[1].getText())

            self.constructed_messages[var_name] = message_dict
            return "".join(snapshots) if snapshots else None
        elif var_name in self.proxy_keys:
            if not str(operation.getChildren()[2]) in self.arch.global_arch.network.base_message_dict:
                return f"//Skipped {var_name} := {str(operation.getChildren()[2])}"
            right_side, right_type = self.gen_right_assignment(operation.getChildren()[2])
            assert right_type == ProtoParserBase.t_msg
            result = ""
            for m in Util.proxy_key_fields(self.arch, var_name).keys():
                result += Util.get_entry_variable(self.arch, self.cache, var_name, f"{var_name}_{m} := {right_side}.{SLICCTokens.field_map.get(m, m)}" + self.end)
            return result
        elif var_name in self.arch.machine.variables and self._partial_source(operation) is not None:
            data, mask = self._partial_source(operation)
            return f"mergeCacheBlock(tbe, getEntry(LineAddress), LineAddress, {data}, {mask}){self.end}"
        elif var_name in self.arch.machine.variables:
            # return Util.get_entry_variable(self.arch, self.cache, var_name,
            #                                self._exist_var_assignment(var_name, operation))
            if (self.arch.machine.mach_id == "cache"):
                if var_name == Util.get_active_cache_line(self.arch):
                    return Util.get_entry_variable(self.arch, self.cache, var_name, 'cl_in_msg')
                else:
                    return Util.get_entry_variable(self.arch, self.cache, var_name,
                                                   self._exist_var_assignment(var_name, operation))
            else:
                return Util.get_entry_variable(self.arch, self.cache, var_name, self._exist_var_assignment(var_name, operation))
        elif var_name in self.local_variables:
            # Variable is local (in the scope)
            return self._exist_var_assignment(var_name, operation)
        else:
            # Create new local variable, keep track of type for future type checking
            # Type check right hand side of the assignment
            assign_str, data_type = self.gen_right_assignment(operation.getChildren()[2])
            self.local_variables[var_name] = data_type
            return var_name + " := " + assign_str + self.end

    def _write_mask(self, msg_name: str) -> str:
        """The write mask of a partial message: that of the store of release-consistency code or of
        the partial message being served, or that of the deferred request of a proxy."""
        if Util.is_rc_store(self.cur_guard_str) \
                or self.cur_guard_str in Util.partial_messages(self.arch.global_arch):
            return f"{SLICCTokens.k_in_msg}.{SLICCTokens.write_mask}"
        keys = sorted(self.proxy_keys)
        assert keys, f"{msg_name}: no write mask to send in {self.arch} on {self.cur_guard_str}"
        key = next((k for k in keys if msg_name.endswith(k[len("proxy_msg"):])), keys[0])
        return Util.get_entry_variable(self.arch, self.cache, key, f"{key}_{SLICCTokens.write_mask}")

    def _partial_source(self, operation: CommonTree) -> Union[Tuple[str, str], None]:
        """(data, write mask) if the operation assigns the cache line from a partial message: the one
        being served, or the deferred request of a proxy when the protocol has partial messages (a
        deferred request that is not partial has an empty mask, which merges the whole block)."""
        partial = Util.partial_messages(self.arch.global_arch)
        if not partial or str(operation.getChildren()[0]) != Util.get_active_cache_line(self.arch):
            return None
        right = operation.getChildren()[2]
        source = str(right)
        data_var = Util.get_message_data_var(self.arch.global_arch)
        if "".join(childsToStringList(right))[1:] != data_var:
            return None
        if source == self.cur_guard_str and source in partial:
            return f"{SLICCTokens.k_in_msg}.{data_var}", f"{SLICCTokens.k_in_msg}.{SLICCTokens.write_mask}"
        if source in self.proxy_keys:
            return (Util.get_entry_variable(self.arch, self.cache, source, f"{source}_{data_var}"),
                    Util.get_entry_variable(self.arch, self.cache, source, f"{source}_{SLICCTokens.write_mask}"))
        return None

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

                # Ensure that the type of the variable is consistent
                self.perror("Variable: " + var_name + " is used for different data types: " +
                            str(data_type) + " | " + str(rev_var_type) + "this is not supported by SLICC",
                            str(data_type) == str(rev_var_type))

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
        elif right_assignment in self.constructed_messages:
            msg = self.constructed_messages[right_assignment]
            msg_type = msg["Type"].split(":")[1]
            _, msg_type = self._in_msg_assignment(msg_type, operation)
            field = "".join(childsToStringList(operation))[1:]
            field = SLICCTokens.field_map.get(field, field)
            replacement = msg[field]
            return replacement, msg_type
        elif right_assignment in self.proxy_keys:
            m_name = "".join(childsToStringList(operation))[1:]
            m_type = Util.proxy_key_fields(self.arch, right_assignment)[m_name]
            return Util.get_entry_variable(self.arch, self.cache, right_assignment,  f"{right_assignment}_{m_name}"), m_type
        elif right_assignment in self.arch.machine.variables:
            right_type = self.arch.machine.variables[right_assignment]
            right_value = right_assignment
            if str(right_type) == ProtoParserBase.t_msg and len(operation.getChildren()) > 1:
                field = str(operation.getChildren()[1])
                right_type = SLICCTokens.base_message_vars[field]
                right_value += "." + SLICCTokens.field_map.get(field, field)


            return Util.get_entry_variable(self.arch, self.cache, right_assignment, right_value), right_type
        elif right_assignment in self.local_variables:
            return right_assignment, self.local_variables[right_assignment]

        # Assignment from Guard or Data Type
        elif right_assignment == self.cur_guard_str:
            # The current guard is an in msg
            if right_assignment in self.arch.global_arch.network.base_message_dict:
                return self._in_msg_assignment(right_assignment, operation)
            # The current guard in an event
            else:
                self.perror("EVENTS NOT IMPLEMENTED YET")

        elif right_assignment == ProtoParserBase.k_setfunc:
            return self.gen_set_function(operation), None
        elif right_assignment == ProtoParserBase.k_id:
            return SLICCTokens.k_mach, None
        else:
            return "".join(toStringList(operation)), None

    def _msg_src_dest(self, operation: CommonTree) -> str:
        if str(operation) in self.arch.global_arch.network.base_message_dict:
            field = ''.join(childsToStringList(operation))[1:]
            field = SLICCTokens.field_map.get(field, field)
            return f"{SLICCTokens.k_in_msg}.{field}"
        elif str(operation) in self.proxy_keys:
            m_name = "".join(childsToStringList(operation))[1:]
            return Util.get_entry_variable(self.arch, self.cache, str(operation),f"{str(operation)}_{m_name}")
        elif str(operation) in self.arch.machine.variables:
            right_value = str(operation)
            right_type = self.arch.machine.variables[right_value]
            if str(right_type) == ProtoParserBase.t_msg and len(operation.getChildren()) > 1:
                field = str(operation.getChildren()[1])
                right_value += "." + SLICCTokens.field_map.get(field, field)
            return Util.get_entry_variable(self.arch, self.cache, str(operation), right_value)
        elif str(operation) in self.machine_mappings:
            if str(operation) == str(self.arch):
                return SLICCTokens.k_mach
            keys = list(self.machine_mappings.keys())
            idx = keys.index(self.arch.arch_name)
            if idx < len(keys) - 2:
                next_key = keys[idx + 1]
                mt = self.machine_mappings[next_key]
                if OPTIONS.llc_mapping in (LLC_BANKED, LLC_RANGE):
                    return (f"mapAddressToRange(LineAddress, MachineType:{mt}, l2_select_low_bit, "
                            f"l2_select_num_bits, intToID({mt}_id))")
                return f"createMachineID(MachineType:{mt},intToID({mt}_id))"
            else:
                return f"mapAddressToMachine(LineAddress, MachineType:{self.machine_mappings[str(operation)]})"
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

            field = ''.join(childsToStringList(operation))[1:]
            field = SLICCTokens.field_map.get(field, field)
            return f"{SLICCTokens.k_in_msg}.{field}", var_type

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
    def gen_final_state(temp_h: TemplateHandler, state: str, cache: bool) -> str:

        if cache:
            return f"setState(tbe, getEntry(LineAddress), LineAddress, State:{state})" \
                   f"{temp_h.end}"
        else:
            return f"setState(tbe, LineAddress, State:{state}){temp_h.end}"

    @staticmethod
    def gen_pop_net(temp_h: TemplateHandler, port_name: str) -> str:
        return (f'DPRINTF(RubySlicc, "Popping %s %s on {port_name} (addr: %#x)\\\\n", in_msg.Type, in_msg.Sender, LineAddress);{temp_h.nl}' if not "mandatory" in port_name else "") + \
            f"{port_name}.dequeue(clockEdge()){temp_h.end}"

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

    @staticmethod
    def _gen_vector_smallest(*args: List[str]) -> str:
        return f"{args[0]}.smallestElement()"
