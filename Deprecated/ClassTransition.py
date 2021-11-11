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
from typing import List, Union, Tuple

import copy

from DataObjects.FlowDataTypes.ClassMessage import Message
from DataObjects.ClassBaseState import SSPState

from Algorithms.General.AuxStateHandler import AuxStateHandler

from Parser.CopyReducedCommonTree import copy_tree


class Transition:
    def __init__(self, startstate, finalstate, access='', inmsg='', outmsg='', cond='', operation=''):

        if access:
            assert isinstance(access, str) or isinstance(access, Message)

        if not startstate.testaccess(access) and inmsg == '':
            self.inMsg: str = access
            self.access: str = ''
        else:
            self.access: str = access
            self.inMsg: str = inmsg

        if inmsg:
            assert isinstance(inmsg, Message)

        if isinstance(outmsg, list) and all(isinstance(msg, Message) for msg in outmsg):
            self.outMsg: List[Message] = outmsg
        elif isinstance(outmsg, Message):
            self.outMsg: List[Message] = [outmsg]
        elif outmsg == '':
            self.outMsg: List[Message] = []
        else:
            assert 0, "Unknown output message format"

        if operation:
            if isinstance(operation, list):
                assert all(isinstance(entry, CommonTree) for entry in operation)
                self.operation: List[CommonTree] = operation
            else:
                assert isinstance(operation, CommonTree)
                self.operation: List[CommonTree] = [operation]
        else:
            self.operation: List[CommonTree] = []

        # The cond field is used by ProtoGen do determine whether concurrency was already introduced to a state,
        # by comparing transition guards and conditions
        # The operation field is vital for the correctness of the parser
        if cond:
            if isinstance(cond, list):
                assert all(isinstance(entry, str) for entry in cond)
                self.cond: List[str] = cond
            else:
                assert all(isinstance(entry, CommonTree) for entry in cond)
                self.cond = [cond]
        else:
            self.cond = []

        self.comm_class = None
        self.access_class = TransitionClassificationEnum.invalid    # UNUSED
        self.start_state: Union[SSPState, 'State'] = startstate
        self.final_state: Union[SSPState, 'State'] = finalstate

        # The defermsg contains the name of the deferred messages and the deferred operations actually contain
        # the operations that need to be performed
        self.defermsg = []
        self.deferred_operations = []

        self.refguard = ''

    def __str__(self):
        return str(self.start_state) + " -- " + str(self.inMsg) + str(self.access) + " -> " + str(self.final_state)

    def get_hash(self):
        return hash((str(self.start_state), str(self.final_state), str(self.access), str(self.inMsg),
                     str([str(operation) for operation in self.operation])))

    # The outgoing msgs do not matter for the path taken, but only the responses do
    def get_msg_hash(self) -> Tuple[str, str]:                 #Tuple[str]]:
        return str(self.access), str(self.inMsg)
        #return str(self.access), str(self.inMsg), tuple(sorted([str(out_msg) for out_msg in self.outMsg]))

    def get_hash_ignore_finale_state(self):
        return hash((str(self.start_state), str(self.access), str(self.inMsg),
                     str([str(operation) for operation in self.operation])))

    def get_hash_ignore_states(self):
        return hash((str(self.access), str(self.inMsg), str([str(operation) for operation in self.operation])))

########################################################################################################################
# SETUP FUNCTIONS
########################################################################################################################
    def addoperation(self, treenode):
        assert isinstance(treenode, CommonTree)
        self.operation.append(treenode)

    def add_operation_list(self, operations: List[CommonTree]):
        self.operation += operations

    def getoperation(self):
        return self.operation

    def setstartstate(self, startstate: Union[SSPState, 'State']):
        self.start_state = startstate

    def getstartstate(self):
        return self.start_state

    def setfinalstate(self, finalstate: Union[SSPState, 'State']):
        self.final_state = finalstate

    def getfinalstate(self):
        return self.final_state

    def getaccess(self) -> str:
        return self.access

    def getinmsg(self) -> str:
        return self.inMsg

    def setinmsg(self, inmsg: Message):
        assert isinstance(inmsg, Message)
        self.inMsg = inmsg

    def addoutmsg(self, message: Message):
        assert isinstance(message, Message)
        self.outMsg.append(message)

    def getoutmsg(self) -> List[Message]:
        return self.outMsg

    def add_out_msg_list(self, out_msg: Union[Message, List[Message]]):
        if isinstance(out_msg, List):
            self.outMsg += out_msg
        else:
            assert isinstance(out_msg, Message)
            self.outMsg += [out_msg]

    def deferoutmsg(self, defermsgs=0) -> List[str]:
        if not defermsgs:
            msg = self.outMsg
            self.outMsg = []
            self.defermsg += [entry for entry in msg if entry not in self.defermsg]
            return msg

        else:
            newoutmsg = []
            defermsg = []
            for msg in self.outMsg:
                if isinstance(msg, Message):
                    msgid = msg.getmsgtype()
                else:
                    msgid = msg
                if msgid in defermsgs:
                    defermsg.append(msg)
                else:
                    newoutmsg.append(msg)

            self.defermsg += [entry for entry in defermsg if entry not in self.defermsg]
            self.outMsg = newoutmsg

            return defermsg

    def set_out_msg(self, out_msg_list: List['State']):
        self.outMsg = out_msg_list

    def getdefermsg(self):
        return self.defermsg

    def getguard(self):
        if self.inMsg:
            if isinstance(self.inMsg, Message):
                guard = self.inMsg.getmsgtype()
            else:
                guard = self.inMsg
        else:
            guard = self.access

        #if self.access:
        #    guard = self.access
        #else:
        #    if isinstance(self.inMsg, Message):
        #        guard = self.inMsg.getmsgtype()
        #    else:
        #        guard = self.inMsg
        return guard

    def getrefguard(self):
        return self.refguard

    def addcond(self, cond):
        self.cond.append(cond)

    def getcond(self):
        return self.cond

    def getoutmsgrenamed(self):
        return self.outmsgrename

    def getoutmsgtypes(self):
        msgouttypes = []
        for message in self.outMsg:
            if isinstance(message, str):
                msgouttypes.append(message)
            else:
                msgouttypes.append(message.getmsgtype())
        return msgouttypes

    def rename_inmsg_operation(self, msg_name: str, new_msg_name: str):
        if msg_name == str(self.inMsg):
            self.rename_in_msg(msg_name, new_msg_name)
            # update all message tokens
            self.rename_operation(msg_name, new_msg_name)

    def rename_outmsg_operation(self, msg_name: str, new_msg_name: str):
        self.rename_out_msg(msg_name, new_msg_name)
        # update all message tokens
        self.rename_operation(msg_name, new_msg_name)

    def rename_operation(self, cur_var: str, new_var: str):
        self.operation = AuxStateHandler.cond_operations_var_rename(self.operation, cur_var, new_var)

    def rename_in_msg(self, msg_name: str, new_msg_name: str):
        if isinstance(self.inMsg, Message):
            self.inMsg.id = new_msg_name
        else:
            self.inMsg = new_msg_name

    def rename_out_msg(self, msg_name: str, new_msg_name: str):
        for outMsg in self.outMsg:
            if str(outMsg) == msg_name:
                outMsg.id = new_msg_name

    ####################################################################################################################
    # COMMON
    ####################################################################################################################

    def copy_modify_trans(self, startstate: 'State', finalstate: 'State'):
        newtrans = copy.copy(self)
        newtrans.setstartstate(startstate)
        newtrans.setfinalstate(finalstate)
        return newtrans

    def deepcopy_modify_trans(self):
        newtrans = copy.copy(self)
        newtrans.access_class = copy.copy(self.access_class)
        newtrans.access = copy.copy(self.access)
        newtrans.inMsg = copy.copy(self.inMsg)
        newtrans.outMsg = copy.copy(self.outMsg)
        newtrans.operation = [copy_tree(operation) for operation in self.operation]
        newtrans.cond = copy.copy(self.cond)
        return newtrans

    ####################################################################################################################
    # HieraGen functions
    ####################################################################################################################

    def update_state_str(self, str_id: str):
        self.update_start_state_id(str_id)
        self.update_final_state_id(str_id)

    def update_start_state_id(self, str_id: str):
        self.start_state.state = str_id + "_" + self.start_state.state

    def update_final_state_id(self, str_id: str):
        self.final_state.state = str_id + "_" + self.final_state.state

########################################################################################################################
# DEBUG FUNCTIONS
########################################################################################################################

    def pbase(self):
        return ("Transition:: SS: " + self.start_state.pstate() +
                "  FS: " + self.final_state.pstate() +
                " Guard: " + str(self.getguard()))

