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

from typing import List

from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess
from DataObjects.Transitions.ClassTransitionv2 import Event
from Parser.ProtoCCcomTreeFct import objListToStringList
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2

from Debug.Monitor.ClassDebug import Debug


class ProtoCCTablePrinter(Debug):

    Spacing = 20
    TransFormat = ["StartState", "FinalState", "Access", "InMsg", "InEvent", "OutMsg", "OutEvent", "Cond"]

    def __init__(self, debug_enable: bool = True):
        Debug.__init__(self, debug_enable)

    def ptransition(self, transition: Transition_v2):
        self.ptable(self.TransFormat, [self.outtransition(transition)])

    def ptransitiontable(self, transitions: List[Transition_v2]):
        states = []
        for transition in transitions:
            states.append(str(transition.start_state))
            states.append(str(transition.final_state))
        states = list(set(states))
        self.p_header("#States: " + str(len(states)) + "   #Transitions: " + str(len(transitions)))

        output = []
        for transition in sorted(transitions, key=lambda x: str(x)):
            output.append(self.outtransition(transition))
        self.ptable(self.TransFormat, output)

    @staticmethod
    def outtransition(transition: Transition_v2) -> List[str]:
        p_start_state = str(transition.start_state)
        p_final_state = str(transition.final_state)

        p_access: str = ""
        p_in_msg: str = ""
        p_event: str = ""
        if isinstance(transition.guard, Event):
            p_event = str(transition.guard)
        else:
            if isinstance(transition.guard, BaseAccess.Access_type):
                p_access = str(transition.guard)
            else:
                p_in_msg = str(transition.guard)

        p_out_msg: str = ""
        p_out_event: str = ""
        for out_msg in transition.out_msg:
            if p_out_msg != "":
                p_out_msg += "; "

            if p_out_event != "":
                p_out_event += "; "

            if isinstance(out_msg, Event):
                p_out_event += str(out_msg)
            else:
                p_out_msg += str(out_msg) + "@" + str(out_msg.get_vc())

        p_cond = ""
        for cond in transition.dbg_cond_operation():
            if p_cond != "":
                p_cond += "; "
            p_cond += ''.join(cond)

        return [p_start_state, p_final_state, p_access, p_in_msg, p_event, p_out_msg, p_out_event, p_cond]

    @staticmethod
    def ptransaction(transactions):
        for transaction in transactions:
            ProtoCCTablePrinter().ptransitions(transaction.gettransitions())

    def ptransitions(self, transitions):
        for transition in transitions:
            ProtoCCTablePrinter().ptransition(transition)
            self.pdebug('$')
            ops = objListToStringList(transition.getoperation())
            for entry in ops:
                self.pdebug(entry)
            self.pdebug()

    def pstates(self, states):
        for state in states:
            self.p_header('$$$$' + state.getstatename())
            self.ptransitions(state.gettransitions())
