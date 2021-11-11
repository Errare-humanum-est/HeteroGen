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

import os
from typing import List
from graphviz import Digraph
from Debug.Monitor.ProtoCCTable import ProtoCCTablePrinter

from DataObjects.Transitions.ClassTransitionv2 import Transition_v2


class ProtoCCGraph:

    EdgeFontSizeInt = '10'
    EdgeFontSizeLoop = '8'
    NodeFontSizeLoop = '12'
    TextFontSize = '15'

    def __init__(self, header: str, transitions: List[Transition_v2], option=0):
        # Compass points currently not used, as not more than 4 loops were observed
        # CompassPoints=["n","ne","e","se","s","sw","w","nw","c","_"]

        # Create FSM graphs
        self.graph = Digraph(header, filename=(header + '.gv'), engine='dot')
        # Use Splines and resolve Node overlapping
        self.graph.attr(splines='true')
        # Graph direction
        self.graph.attr(rankdir='LR')  # 'LR'
        # Internode and edge spacing

        if option == 0:
            self.graph.attr(nodesep='0.4', ranksep='2')
            self.graph.attr(ratio='0.5')
        else:
            self.graph.attr(nodesep='0.1', ranksep='0.3')
            self.graph.attr(ratio='0.2')

        # Label[RespMsg,FinalState]
        self.graph.attr(label=header, fontsize=self.TextFontSize)

        self._ptransitions(transitions)
        self.graph.view(header, os.getcwd(), False)

    def _ptransitions(self, transitions: List[Transition_v2], color='black'):
        for entry in transitions:
            start_state, final_state, access, p_in_msg, p_in_event, p_out_msg, p_out_event, p_cond = \
                ProtoCCTablePrinter.outtransition(entry)
            
            guardstr = ""
            if access:
                guardstr += "*" + access
            if p_in_msg:
                if access:
                    guardstr += "; "
                guardstr += "<" + p_in_msg
            if p_in_event:
                if access:
                    guardstr += "; "
                guardstr += "<" + p_in_event

            if p_cond:
                guardstr += "; (" + p_cond + ") "
            if p_out_msg:
                guardstr += "; >" + p_out_msg
            if p_out_event:
                guardstr += "; >" + p_out_event
            if entry.comm_class:
                guardstr += " || " + str(entry.comm_class)

            self.graph.edge(start_state,
                            final_state,
                            guardstr,
                            fontsize=self.EdgeFontSizeInt,
                            fontcolor=color
                            )
