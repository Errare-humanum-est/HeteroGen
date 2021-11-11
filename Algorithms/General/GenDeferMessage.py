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
#

import copy
from typing import Dict, Tuple

from Deprecated.ClassTransition import Transition
from DataObjects.FlowDataTypes.ClassMessage import Message

from antlr3.tree import CommonToken
from Parser.ProtoCCcomTreeFct import *
from Murphi.MurphiModular import MurphiModular

from DataObjects.ClassProtoCCObject import PCCObject


class GenDeferMessage:

    def __init__(self):
        # Get global variables
        pass

    # Complete conservative deferring
    def defer_push_message(self, defer_transition: Transition, defer_token: str) -> CommonTree:
        new_operation = CommonTree(CommonToken(text=defer_token))
        new_operation.addChild(CommonTree(CommonToken(text="recv")))
        new_operation.addChild(CommonTree(CommonToken(text=str(defer_transition.inMsg))))
        return new_operation

    def defer_pop_message(self, defer_transition: Transition, defer_token: str) -> CommonTree:
        new_operation = CommonTree(CommonToken(text=MurphiModular.tASSIGN))

        # Left side assignment
        new_operation.addChild(CommonTree(CommonToken(text=str(defer_transition.inMsg))))
        # Assignment operator
        new_operation.addChild(CommonTree(CommonToken(text="=")))
        # Right side assignment
        new_operation.addChild(CommonTree(CommonToken(text=defer_token)))

        return new_operation

    def gen_defer_message(self,
                          defer_transitions: List[Transition],
                          defer_msg_list: Dict[CommonTree, List[str]],
                          message_objects: List[PCCObject]) \
            -> Dict[Transition, List[Tuple[Message, List[CommonTree]]]]:

        defer_msg_objects: Dict[Transition, List[Tuple[Message, List[CommonTree]]]] = {}

        # Only messages in defer messages need to be deferred and operations dependent on them
        # Extract from variable dependence which ssp_transitions need to be deferred

        for transition in defer_transitions:

            # Dynamic (are allowed to be cleared)
            # Left assignment of defer message
            defer_var_msgvar_names: Dict[str, str] = {}
            # variables dependent on defer_var_msg_name
            dependent_defer_msg_vars: Dict[str, str] = {}

            # Necessary to track the exact order in which messages were normally sent
            defer_message_operation_dict: Dict[str, List[CommonTree]] = {}

            # Return tuple
            defer_message_operation_sequence: List[Tuple[str, List[CommonTree]]] = []

            for trans_operation in transition.operation:
                # Msg defer assignment operation found in transition list
                if trans_operation in defer_msg_list:

                    # Defer the message
                    defer_operations = self.defer_msg_assignment(trans_operation,
                                                                 defer_msg_list[trans_operation],
                                                                 message_objects)

                    children = trans_operation.getChildren()
                    defer_var_name = MurphiModular.vdeferpref + str(children[0]) + "_" + str(children[2].children[1])
                    # Records the variable name of the child
                    defer_var_msgvar_names[str(children[0])] = defer_var_name
                    defer_message_operation_sequence.append((str(children[2].children[1]), defer_operations))
                    defer_message_operation_dict[str(children[0])] = defer_operations

                # Defer the sending function
                elif str(trans_operation) == MurphiModular.tSEND:
                    children = trans_operation.getChildren()
                    if str(children[1]) in defer_message_operation_dict:
                        children = trans_operation.getChildren()
                        defer_operations = self.defer_send_function(transition, trans_operation, defer_var_msgvar_names)
                        defer_message_operation_dict[str(children[1])] += defer_operations

                elif str(trans_operation) == MurphiModular.tASSIGN:
                    self.defer_left_dependent_operations(trans_operation,
                                                         defer_var_msgvar_names,
                                                         dependent_defer_msg_vars,
                                                         defer_message_operation_dict)

            transition.operation = copy.copy(transition.operation)
            transition.outMsg = copy.copy(transition.outMsg)

            result_tuples = []
            # The defer operations were found, now update the tokens so they are deferred
            for defer_entry in defer_message_operation_sequence:
                for out_msg in transition.outMsg:
                    if str(out_msg) == defer_entry[0]:
                        result_tuples.append((out_msg, defer_entry[1]))
                        transition.outMsg.remove(out_msg)
                        break

            if defer_message_operation_sequence:
                defer_msg_objects[transition] = result_tuples

        return defer_msg_objects

    # Defer tMSGCSTR e.g. local_var = Resp(GetM, .....)
    def defer_msg_assignment(self,
                             trans_operation: CommonTree,
                             defer_msg_list_dependent_var: List[str],
                             message_objects: List[PCCObject]) -> List[CommonTree]:

        local_defer_operations = []

        children = trans_operation.getChildren()

        # Retrieve deferred operation
        tmp_operation = copy.deepcopy(trans_operation)
        tmp_children = tmp_operation.getChildren()
        defer_var_name = MurphiModular.vdeferpref + str(children[0]) + "_" + \
                         str(children[2].children[1])
        tmp_children[0].token.text = defer_var_name
        tmp_children[2].token.text = MurphiModular.tPOP_HL_DEFER
        local_defer_operations.append(tmp_operation)

        local_defer_operations += self.update_messages(trans_operation, defer_msg_list_dependent_var, message_objects)

        return local_defer_operations

    def update_messages(self,
                        trans_operation: CommonTree,
                        defer_msg_list_dependent_var: List[str],
                        message_objects: List[PCCObject]) -> List[CommonTree]:

        local_update_operations = []
        children = trans_operation.getChildren()
        defer_var_name = MurphiModular.vdeferpref + str(children[0]) + "_" + str(children[2].children[1])
        in_msg_name = str(children[2].children[1])

        # Update the variables in the deferred message retrieved from buffer
        if len(children[2].children) > 4:   # Not a base message
            payload = children[2].children[4:]
            # Get the index of the dependent variable in message constructor
            for var_ind in range(0, len(payload)):
                local_var_name = str(payload[var_ind])
                # Check if there exists a message dependency
                if local_var_name in defer_msg_list_dependent_var:
                    # Find the message constructor
                    for message_object in message_objects:
                        # The right constructor was found
                        if str(message_object) == str(children[2].children[0]):
                            msg_object = message_object.structure.children[var_ind+1]
                            msg_var = str(msg_object)
                            local_update_operations.append(self.generate_update_assignement(defer_var_name,
                                                                                            msg_var,
                                                                                            local_var_name,
                                                                                            in_msg_name))
        return local_update_operations

    def generate_update_assignement(self,
                                    defer_var_name: str,
                                    msg_var: str,
                                    local_var_name: str,
                                    in_msg_name: str=""):

        new_operation = CommonTree(CommonToken(text=MurphiModular.tASSIGN))

        # Left side assignment
        left_tree = CommonTree(CommonToken(text=defer_var_name))
        left_tree.addChild(CommonTree(CommonToken(text=".")))
        left_tree.addChild(CommonTree(CommonToken(text=msg_var)))
        new_operation.addChild(left_tree)

        new_operation.addChild(CommonTree(CommonToken(text="=")))

        # Right side assignment
        new_operation.addChild(CommonTree(CommonToken(text=local_var_name)))
        #left_tree = CommonTree(CommonToken(text=in_msg_name))
        #left_tree.addChild(CommonTree(CommonToken(text=".")))
        #left_tree.addChild(CommonTree(CommonToken(text=msg_var)))
        return new_operation


    def defer_send_function(self,
                            transition: Transition,
                            trans_operation: CommonTree,
                            var_names: Dict[str, str]) -> List[CommonTree]:
        children = trans_operation.getChildren()
        if str(children[1]) in var_names:
            ret_operation = copy.deepcopy(trans_operation)
            ret_operation.children[1].token.text = var_names[str(children[1])]
            tmp_operation = copy.deepcopy(trans_operation)
            tmp_operation.token.text = MurphiModular.tPUSH_HL_DEFER
            transition.operation = copy.copy(transition.operation)
            transition.operation[transition.operation.index(trans_operation)] = tmp_operation
            return [ret_operation]
        return []


    def defer_left_dependent_operations(self,
                                        trans_operation: CommonTree,
                                        defer_msg_var_names: Dict[str, str],
                                        dependent_defer_msg_vars: Dict[str, str],
                                        defer_message_operation_dict: Dict[str, List[CommonTree]]
                                        ):
        children = trans_operation.getChildren()
        cur_var_name = str(children[0])

        # Left assignment
        # Remove [ASSIGN, var_name, = ]
        assignment_list = toStringList(trans_operation)[3:]
        # Variable reassignment e.g. new Msg object assigned to same var
        if cur_var_name in defer_msg_var_names and cur_var_name not in assignment_list:
            remove_var = defer_msg_var_names.pop(cur_var_name)
            del defer_message_operation_dict[cur_var_name]

            remove_key_list = []
            # Clear dependent variables
            for dependent_var_name in dependent_defer_msg_vars:
                if dependent_defer_msg_vars[dependent_var_name] == remove_var:
                    remove_key_list.append(dependent_var_name)

            for key in remove_key_list:
                del dependent_defer_msg_vars[key]

        else:
            for var_name in defer_msg_var_names:

                # Current value of variable is used in an assignment
                if var_name in assignment_list:
                    dependent_defer_msg_vars[(children[0])] = var_name
                    defer_message_operation_dict[var_name].append(trans_operation)
                    continue

                for dependent_var_name in dependent_defer_msg_vars:
                    if dependent_var_name in assignment_list:
                        dependent_defer_msg_vars[(children[0])] = var_name
                        defer_message_operation_dict[var_name].append(trans_operation)


    # Searches for the assignment of specific messages
    def find_message_assign(self, messages: List[Message], defer_transitions: List[Transition]) -> List[CommonTree]:
        defer_message_assign = []
        messages = [str(message) for message in messages]

        for transition in defer_transitions:
            found_messages = []
            for trans_operation in transition.operation:
                if str(trans_operation) == MurphiModular.tASSIGN:
                    children = trans_operation.getChildren()
                    if str(children[2]) == MurphiModular.tMSGCSTR:
                        if str(children[2].children[1]) in messages:
                            defer_message_assign.append(trans_operation)
                            found_messages.append(str(children[2].children[1]))

        return defer_message_assign


    '''#################################################################################################################
    # BASE MESSAGE DEFER
    #################################################################################################################'''
    def defer_base_message(self,
                           trans_operation: CommonTree,
                           transition: Transition,
                           var_names: Dict[str, str]) -> List[CommonTree]:
        local_defer_operations = []

        children = trans_operation.getChildren()

        defer_var_name = MurphiModular.vdeferpref + str(children[0]) + "_" + \
                         str(children[2].children[1])
        # Records the variable name of the child
        var_names[str(children[0])] = defer_var_name

        # Recover next deferred operation
        tmp_operation = copy.deepcopy(trans_operation)
        tmp_children = tmp_operation.getChildren()
        defer_var_name = MurphiModular.vdeferpref + str(tmp_children[0]) + "_" + \
                         str(tmp_children[2].children[1])
        tmp_children[0].token.text = defer_var_name
        tmp_children[2].token.text = MurphiModular.tPOP_HL_DEFER
        local_defer_operations.append(tmp_operation)

        # Construct Original Message from deferred operation
        tmp_operation = copy.deepcopy(trans_operation)
        tmp_children = tmp_operation.getChildren()
        tmp_children[2].token.text = MurphiModular.tSEND_BASE_DEFER
        tmp_children[2].children[1].token.text = defer_var_name
        for ind in range(2, len(MurphiModular.BaseMsg)):
            tmp_children[2].children.pop(2)

        local_defer_operations.append(tmp_operation)

        tmp_operation = copy.deepcopy(trans_operation)
        tmp_children = tmp_operation.getChildren()

        # Generate BaseMessage that is deferred
        tmp_children[0].token.text = defer_var_name
        tmp_children[2].token.text = MurphiModular.tSEND_BASE_DEFER
        tmp_children[2].children[0].token.text = MurphiModular.rbasemessage
        for ind in range(len(MurphiModular.BaseMsg), len(tmp_children[2].getChildren())):
            tmp_children[2].children.pop(len(MurphiModular.BaseMsg))

        # Update the transition
        transition.operation = copy.copy(transition.operation)
        transition.operation[transition.operation.index(trans_operation)] = tmp_operation

        return local_defer_operations

    def send_base_message(self,
                          trans_operation: CommonTree,
                          transition: Transition,
                          var_names: Dict[str, str]) -> List[CommonTree]:
        ret_operation = trans_operation
        children = trans_operation.getChildren()
        if str(children[1]) in var_names:
            tmp_operation = copy.deepcopy(trans_operation)
            tmp_operation.token.text = MurphiModular.tPUSH_HL_DEFER
            tmp_operation.children[1].token.text = var_names[str(children[1])]
            transition.operation = copy.copy(transition.operation)
            transition.operation[transition.operation.index(trans_operation)] = tmp_operation
            return [ret_operation]
        return []










