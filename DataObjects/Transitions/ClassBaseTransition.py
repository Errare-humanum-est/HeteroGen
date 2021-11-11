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
from typing import List, Union, Set
from copy import copy

from DataObjects.FlowDataTypes.ClassMessage import Message
from DataObjects.FlowDataTypes.ClassEvent import Event, EventAck
from DataObjects.ClassBaseState import SSPState

from Parser.DataTypes.ClassGuard import Guard
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from Parser.ProtoCCcomTreeFct import objListToStringList

from Parser.CopyReducedCommonTree import copy_tree

from DataObjects.FlowDataTypes.ClassBaseAccess import Access, Evict
from Parser.ProtoCCcomTreeFct import toStringList

from Algorithms.General.AuxStateHandler import AuxStateHandler


class BaseTransition:
    def __init__(self,
                 start_state: Union[SSPState, 'State_v2'],
                 final_state: Union[SSPState, 'State_v2'],
                 operations: List[CommonTree],
                 guard: Union[Message, Event, EventAck, Access, Evict, Guard],
                 out_msg: List[Message] = None,
                 out_event: Event = None):

        self.start_state: Union[SSPState, 'State_v2'] = start_state
        self.final_state: Union[SSPState, 'State_v2'] = final_state

        self.operations: List[CommonTree] = operations

        self.guard: Union[Message, Event, EventAck, Access, Evict, Guard] = guard

        self.out_msg: List[Message] = out_msg
        # A transition can cause a single internal event
        self.out_event: Event = out_event

        #if hasattr(start_state, 'add_transition'):
        #    start_state.add_transition(self)

    def __str__(self):
        return str(self.start_state) + " -- " + str(self.guard) + " -> " + str(self.final_state)

    ## Hash functions
    #
    def __hash__(self):
        return hash((str(self.start_state), str(self.final_state), str(self.guard),
                     '.'.join(objListToStringList(self.operations))))

    def __eq__(self, other):
        return (str(self.start_state) == str(other.start_state) and
                str(self.final_state) == str(other.final_state) and
                str(self.guard) == str(other.guard) and
                str(objListToStringList(self.operations)) == str(objListToStringList(other.operations))
                )

    ## Hash function used by ProtoGen
    #  None
    def get_hash_ignore_states(self):
        return hash((str(self.guard), str([str(operation) for operation in self.operations])))

    ## Front end state generation function
    # Dependency: ClassProtoArchitecture
    def replace_start_state(self, new_state: Union[SSPState, 'State_v2']):
        self.start_state.remove_transitions(self)
        self.start_state = new_state
        self.start_state.add_transitions(self)

    ## Front end state generation function
    # Dependency: ClassProtoArchitecture
    def replace_final_state(self, new_state: Union[SSPState, 'State_v2']):
        # The final states do not track the incoming ssp_transitions
        self.final_state = new_state

    ####################################################################################################################
    # Renaming
    ####################################################################################################################
    def rename_operation(self, cur_var: str, new_var: str):
        AuxStateHandler.cond_operations_var_rename(self.operations, cur_var, new_var)

    def update_state(self, cur_state: 'State_v2', new_state: 'State_v2'):
        if self.start_state == cur_state:
            self.replace_start_state(new_state)
        if self.final_state == cur_state:
            self.final_state = new_state

    ####################################################################################################################
    # ProtoGen (Extract operations)
    ####################################################################################################################
    def extract_cond_operations(self, guard: str = '') -> Set[str]:
        cond_op_set: Set[str] = set()

        for operation in self.operations:
            if str(operation) == ProtoParserBase.k_cond or str(operation) == ProtoParserBase.k_ncond:
                str_list = toStringList(operation)
                if guard:
                    if str(guard) in str_list:
                        cond_op_set.add(str(str_list))
                    else:
                        continue
                else:
                    cond_op_set.add(str(str_list))

        return cond_op_set

    ####################################################################################################################
    # COMMON
    ####################################################################################################################

    def copy_modify_trans(self, start_state: 'State_v2', final_state: 'State_v2'):
        newtrans = self.deepcopy_trans()
        newtrans.start_state = start_state
        newtrans.final_state = final_state
        return newtrans

    def deepcopy_trans(self):
        newtrans = copy(self)
        newtrans.out_msg = copy(self.out_msg)
        newtrans.operations = [copy_tree(operation) for operation in self.operations]
        return newtrans

    ####################################################################################################################
    # Debug Functions
    ####################################################################################################################
    def dbg_operations(self):
        return str(objListToStringList(self.operations))

    # Extract list of condition operations as string
    def dbg_cond_operation(self) -> List[str]:
        cond_list: List[str] = []
        for operation in self.operations:
            if str(operation) in ProtoParserBase.CondKeys:
                cond_list.append(toStringList(operation))
        return cond_list
