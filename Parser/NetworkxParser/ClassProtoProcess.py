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

from typing import List, Dict, Union, Tuple

from Parser.NetworkxParser.TransTreeGeneration.ClassProtoTransitionTree import ProcessStateTransFlowTree

from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.FlowDataTypes.ClassEvent import Event, EventAck, EventNetwork
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess

from Parser.DataTypes.ClassGuard import Guard
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase

from Parser.DataTypes.ClassBaseNetwork import BaseNetwork
from Parser.DataTypes.ClassBaseNetwork import BaseMessage
from DataObjects.FlowDataTypes.ClassMessage import MsgRouting
from DataObjects.FlowDataTypes.ClassMessage import Message


class ProtoProcess(ProcessStateTransFlowTree):

    def __init__(self,
                 process_node: CommonTree,
                 base_access: BaseAccess,
                 network: BaseNetwork,
                 event_network: EventNetwork,
                 dbg_graph: bool = False):
        ProcessStateTransFlowTree.__init__(self, process_node, dbg_graph)

        self.base_access = base_access
        self.network: BaseNetwork = network
        self.event_network: EventNetwork = event_network

        self.transitions: List[Transition_v2] = []

        self.gen_transitions()

    ## Generate the ssp_transitions
    #  @param self The object pointer.
    def gen_transitions(self):
        for trans_object in self.trans_object_start_state_id_map:
            start_state = self.trans_object_start_state_id_map[trans_object]
            final_state = self.trans_object_final_state_id_map[trans_object]

            self.map_access_to_base_access(trans_object.object_sequence)
            # It might be the case that a new type of access is detected that differs from the base accesses, that is
            # why these functions must be executed after the map_access_to_base_access function
            trans_guard = self.get_guard(trans_object.start_guard)
            out_msg_list_event = self.outmsg_constr(trans_object.object_sequence)

            pruned_op = self.prune_control_operations(trans_object.object_sequence)

            new_transition = Transition_v2(start_state,
                                           final_state,
                                           pruned_op,               #trans_object.object_sequence,
                                           trans_guard,
                                           *out_msg_list_event)

            self.transitions.append(new_transition)

    @staticmethod
    def prune_control_operations(operations):
        return [operation for operation in operations
                if str(operation) not in ProtoParserBase.ProcessTreeEnd + [ProtoParserBase.k_break]]

    # Determine accesses as accesses or in_msgs and events as generic transition guards, these will be later analyzed
    # and assigned
    def get_guard(self, start_guard: CommonTree) -> Union[EventAck, Guard, BaseAccess.Access, BaseAccess.Evict]:
        # Access guard
        if str(start_guard) == self.k_trans:
            if str(start_guard.getChildren()[1]) in self.base_access.access_map:
                return self.base_access.access_map[str(start_guard.getChildren()[1])]
            else:
                return Guard(str(start_guard.getChildren()[1]))

        # Message, Access or Event guard
        elif str(start_guard) == self.k_guard:
            if str(start_guard.getChildren()[0]) in self.base_access.access_map:
                return self.base_access.access_map[str(start_guard.getChildren()[0])]
            else:
                return Guard(str(start_guard.getChildren()[0]))

        # Event Ack guard
        elif str(start_guard) == self.k_event_ack:
            guard = str(start_guard.getChildren()[0])
            self.perror("Event must not share identifier with access.",
                        not isinstance(guard, BaseAccess.Access) or not isinstance(guard, BaseAccess.Evict))
            return self.event_network.add_new_event(EventAck(guard))
        else:
            self.perror("Unrecognized transition guard type")

    def map_access_to_base_access(self, operations: List[CommonTree]):
        for operation in operations:
            if (str(operation) == self.k_access and
                    str(operation.getChildren()[0] not in self.event_network.event_issue)):
                self.base_access.map_access_to_base_access(self.guard_id, str(operation.getChildren()[0]))

    def outmsg_constr(self, operations: List[CommonTree]) -> Tuple[List[Message], Event]:
        out_msg_list: List[Union[Message, Event]] = []
        out_event: Event = None
        var_base_msg_map: Dict[str, BaseMessage] = {}
        var_route_msg_map: Dict[str, MsgRouting] = {}
        var_tree_def_map: Dict[str, CommonTree] = {}

        for operation in operations:
            # Message constructor
            if str(operation) == self.k_assign:
                assign_obj = operation.getChildren()
                if str(assign_obj[2]) == self.k_msg:
                    var_id = str(assign_obj[0])
                    msg_desc_obj = assign_obj[2].getChildren()

                    # Get msg type from network specification
                    msg_type = self.network.msg_types[str(msg_desc_obj[0])]

                    # Generate local base message
                    var_base_msg_map[var_id] = BaseMessage(str(msg_desc_obj[1]), msg_type, None)
                    # Generate routing description
                    var_route_msg_map[var_id] = MsgRouting(*(str(x) for x in msg_desc_obj[2:4]))
                    # Store message commontree object
                    var_tree_def_map[var_id] = operation

            # Message send
            elif str(operation) == self.k_send or str(operation) in self.kmbcast:
                assign_obj = operation.getChildren()
                var_id = str(assign_obj[1])
                vc = self.network.get_virtual_channel(str(assign_obj[0]))

                self.perror("Message variable undefined", var_id in var_base_msg_map)
                self.perror("Virtual network undefined", vc)

                base_msg = var_base_msg_map[var_id]
                base_msg.set_vc(vc)

                # Register base message with network
                base_msg = self.network.add_new_base_message(base_msg)

                # Register if the message is unicast, multicast or broadcast
                var_route_msg_map[var_id].cast = str(operation)

                # Now construct actual message
                out_msg_list.append(Message(base_msg,
                                            var_tree_def_map[var_id],
                                            var_route_msg_map[var_id]))

                var_base_msg_map.pop(str(assign_obj[1]))

            # Event issue
            elif str(operation) == self.k_event:
                guard = str(operation.getChildren()[0])
                self.perror("Event must not share identifier with access.",
                            not isinstance(guard, BaseAccess.Access) or not isinstance(guard, BaseAccess.Evict))
                self.perror("Per transition only one event is allowed", not out_event)
                out_event = self.event_network.add_new_event(Event(guard))

        self.pwarning("Not all constructed messages were sent", len(var_base_msg_map.keys()) != 0)

        return out_msg_list, out_event


