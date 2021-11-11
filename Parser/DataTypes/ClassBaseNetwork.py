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

from typing import Dict, List, Union
from antlr3.tree import CommonTree
from collections import OrderedDict

from Parser.ProtoCCLexer import tokenNamesMap
from Debug.Monitor.ClassDebug import Debug
from Algorithms.General.AuxStateHandler import AuxStateHandler
from DataObjects.ClassMultiDict import MultiDict
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase


class NetworkType:
    k_ordered = "Ordered"
    k_unordered = "Unordered"

    # Routing variables
    k_src = "src"
    k_dst = "dst"


## MsgType
#
#  Generic message type format, it holds the information defined in the message object definition of pcc files
#  Dependency: None
class MsgType:

    def __init__(self, msg_object: CommonTree):
        children = msg_object.getChildren()
        self.msg_type: str = str(children[0])
        self.msg_vars: OrderedDict[str, CommonTree] = OrderedDict()
        self.data_flag: bool = False

        self.register_var(children)

    def __str__(self):
        return self.msg_type

    def register_var(self, payload_objects: List[CommonTree]):
        for ind in range(1, len(payload_objects)):
            if payload_objects[ind].getText() == ProtoParserBase.k_data:
                self.data_flag = True
            for var_name in payload_objects[ind].getChildren():
                if str(var_name) not in tokenNamesMap.values():
                    self.msg_vars[str(var_name)] = payload_objects[ind]
                    break

    def update_variable_names(self, new_sub_id: str) -> List[str]:
        variable_keys = list(self.msg_vars.keys())
        ret_variable_keys = []

        for ind in range(0, len(variable_keys)):
            variable = variable_keys[ind]
            # Do not rename the cache line
            if str(self.msg_vars[variable]) == ProtoParserBase.k_data:
                # Make a temporary pointer on data object
                tmp_var = self.msg_vars[variable]
                # Clear old dict entry
                self.msg_vars.pop(variable)
                # Preserve position of data object in ordered dict
                self.msg_vars[variable] = tmp_var
                continue
            ret_variable_keys.append(variable)

            # Update dict entry
            self.msg_vars[variable + new_sub_id] = AuxStateHandler.cond_rename_operation(self.msg_vars[variable],
                                                                                         variable,
                                                                                         variable + new_sub_id,
                                                                                         [])
            # Clear old dict entry
            self.msg_vars.pop(variable)

        return ret_variable_keys


## Channel
#
#  Virtual channel in the network
#  Dependency: MsgType
class Channel(NetworkType):

    def __init__(self, vc_name: str, vc_type: str):
        self.vc_name: str = vc_name                              # virtual channel name
        self.vc_type: str = vc_type                              # ordered / unordered
        self.msg_types: List[MsgType] = []                       # Record all message types that are handled by this VC

    def __str__(self):
        return self.vc_name


## BaseMessage
#
#  Generic message format
#  Dependency: MsgType, Channel
class BaseMessage:

    def __init__(self,
                 name: str,
                 msg_type: MsgType = None,
                 vc: Channel = None):

        self.id: str = name
        self.msg_type: MsgType = msg_type

        self.vc: Channel = vc

        # List of message objects that are based on this base message
        self.msg_obj_list: List = []

        if self.vc and self.msg_type not in self.vc.msg_types:
            self.vc.msg_types.append(self.msg_type)  # Add message type to the virtual channel

    def __str__(self):
        return self.id

    def __hash__(self):
        return hash((self.id, str(self.msg_type), str(self.vc)))

    def has_data(self) -> bool:
        if self.msg_type:
            return self.msg_type.data_flag
        return False

    def set_vc(self, vc: Channel):
        self.vc = vc
        if self.vc and self.msg_type not in self.vc.msg_types:
            self.vc.msg_types.append(self.msg_type)  # Add message type to the virtual channel

    def register_message_object(self, msg_object: 'Message'):
        self.msg_obj_list.append(msg_object)

    def remove_message_object(self, msg_object: 'Message') -> bool:
        if msg_object in self.msg_obj_list:
            self.msg_obj_list.remove(msg_object)
            return True
        return False

    def p_message(self):
        return str(self.id) + ', ' + str(self.msg_type) + ', ' + str(self.vc)


## BaseNetwork
#
#  Generic message format
#  Dependency: MsgType, Channel
class BaseNetwork(NetworkType):

    def __init__(self):
        self.network_node: CommonTree = None

        self.ordered_networks: Dict[str, Channel] = {}
        self.unordered_networks: Dict[str, Channel] = {}

        self.msg_types: Dict[str, MsgType] = {}
        self.data_msg_types: Dict[str, MsgType] = {}        # Data msg type names, should be included in the message
                                                            # and is subset of msgNode

        # There must not be two messages with the same message identifiers in different virtual channels or different
        # msg_types
        #self.base_message_dict: Dict[str, BaseMessage] = {}
        self.base_message_dict: MultiDict = MultiDict()

    def gen_virtual_channels(self, network: CommonTree):
        self.network_node = network
        for channel_obj in network.getChildren():
            channel_def = channel_obj.getChildren()

            if str(channel_def[0]) == self.k_unordered and str(channel_def[1]) not in self.unordered_networks:
                Debug.perror("Network has been declared to be ordered before",
                             str(channel_def[1]) not in self.ordered_networks)
                self.unordered_networks[str(channel_def[1])] = Channel(str(channel_def[1]), self.k_unordered)

            if str(channel_def[0]) == self.k_ordered and str(channel_def[1]) not in self.ordered_networks:
                Debug.perror("Network has been declared to be unordered before",
                             str(channel_def[1]) not in self.unordered_networks)
                self.ordered_networks[str(channel_def[1])] = Channel(str(channel_def[1]), self.k_ordered)

    def gen_msg_type(self, msg_object: CommonTree):
        msg_type = MsgType(msg_object)

        self.msg_types[str(msg_type)] = msg_type

        if msg_type.data_flag:
            self.data_msg_types[str(msg_type)] = msg_type

    def get_virtual_channel(self, channel_name: str) -> Union[Channel, None]:
        if channel_name in self.ordered_networks:
            return self.ordered_networks[channel_name]
        elif channel_name in self.unordered_networks:
            return self.unordered_networks[channel_name]
        return None

    def add_new_base_message(self, new_base_message: BaseMessage) -> BaseMessage:
        if str(new_base_message) in self.base_message_dict:
            exist_msgs = self.base_message_dict[str(new_base_message)]

            # Check if exactly the same message already exists
            for exist_msg in exist_msgs:
                if new_base_message.msg_type == exist_msg.msg_type and new_base_message.vc == exist_msg.vc:
                    return exist_msg

            # Otherwise throw warnings
            # The base messages should have the same message type and virtual channel, throw warnings
            Debug.pwarning("Messages have same identifiers, but are of different message type: " +
                           new_base_message.p_message() + ' | ' +
                           exist_msgs[0].p_message(),
                           new_base_message.msg_type == exist_msgs[0].msg_type)
            Debug.pwarning("Messages have same identifiers, but are assigned to different virtual channels: " +
                           new_base_message.p_message() + ' | ' +
                           exist_msgs[0].p_message(),
                           new_base_message.vc == exist_msgs[0].vc)

        self.base_message_dict[str(new_base_message)] = new_base_message
        return new_base_message

    ## By modifying the existing dict all pointers to the dict remain valid and don't need to be updated
    # Dependency: FlatArchitecture
    def update_base_message_names(self, new_sub_id: str):
        for base_msg_name in list(self.base_message_dict.keys()):
            for base_msg in self.base_message_dict[base_msg_name]:
                # Update msg_id_s
                base_msg.id = base_msg.id + new_sub_id
            # Update dict entry
            self.base_message_dict[base_msg_name+new_sub_id] = self.base_message_dict[base_msg_name]
            # Clear old dict entry
            self.base_message_dict.pop(base_msg_name)

    def update_msg_type_names(self, new_sub_id: str):
        msg_types_keys = list(self.msg_types.keys())
        for msg_type in msg_types_keys:
            # Update msg types
            self.msg_types[msg_type].msg_type = self.msg_types[msg_type].msg_type + new_sub_id
            # Update dict entry
            self.msg_types[msg_type + new_sub_id] = self.msg_types[msg_type]

            # Update the variable names
            self.msg_types[msg_type + new_sub_id].update_variable_names(new_sub_id)

            # Clear old dict entry
            self.msg_types.pop(msg_type)

    def modify_variable_names(self, cur_const: str, new_const: str):
        for msg_type in self.msg_types:
            for msg_var in self.msg_types[msg_type].msg_vars:
                msg_var_object = self.msg_types[msg_type].msg_vars[msg_var]
                self.msg_types[msg_type].msg_vars[msg_var] = \
                    AuxStateHandler.cond_rename_operation(msg_var_object, cur_const, new_const)

    def merge_networks(self, other: 'BaseNetwork'):
        self.ordered_networks.update(other.ordered_networks)
        self.unordered_networks.update(other.unordered_networks)

        self.msg_types.update(other.msg_types)
        self.data_msg_types.update(other.data_msg_types)    # Data msg type names, should be included in the message
                                                            # and is subset of msgNode

        for base_message in other.base_message_dict:
            if base_message in self.base_message_dict:
                self.base_message_dict[base_message] += other.base_message_dict[base_message]
            else:
                self.base_message_dict[base_message] = other.base_message_dict[base_message]

    # Print all the messages
    def p_messages(self):
        pass
        #self.p_header("\nMessages")
        #for entry in self.msgTypes:
        #    self.pdebug(entry)
        #self.pdebug('\n')