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
from typing import List, Tuple, Any
from graphviz import Digraph as gDigraph
from networkx import DiGraph as nDigraph

from DataObjects.ClassMultiDict import MultiDict


class ParserPCCGraph:
    EdgeFontSizeInt = '10'
    EdgeFontSizeLoop = '8'
    NodeFontSizeLoop = '12'
    TextFontSize = '15'

    def __init__(self, header: str, edges: List[Tuple[str]], option=0, show_pdf = True):
        # Compass points currently not used, as not more than 4 loops were observed
        # CompassPoints=["n","ne","e","se","s","sw","w","nw","c","_"]

        # Create FSM graphs
        self.graph = gDigraph(header, filename=(header + '.gv'), engine='dot')
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

        self._pedges(edges)

        if show_pdf:
            self.graph.view(header, os.getcwd(), False)
        else:
            self.graph.render(header, os.getcwd())

    def _pedges(self, edges, color='black'):
        multi_state_dict = MultiDict()
        for edge in edges:

            first_node = edge[0]
            if str(first_node) in multi_state_dict:
                if first_node not in multi_state_dict[str(first_node)]:
                    multi_state_dict[str(first_node)] = first_node
            else:
                multi_state_dict[str(first_node)] = first_node

            first_index = str(multi_state_dict[str(first_node)].index(first_node))

            second_node = edge[1]
            if str(second_node) in multi_state_dict:
                if second_node not in multi_state_dict[str(second_node)]:
                    multi_state_dict[str(second_node)] = second_node
            else:
                multi_state_dict[str(second_node)] = second_node

            second_index = str(multi_state_dict[str(second_node)].index(second_node))

            self.graph.edge(str(edge[0]) + first_index,
                            str(edge[1]) + second_index,
                            fontsize=self.EdgeFontSizeInt,
                            fontcolor=color
                            )
    @staticmethod
    def debug_process_graph(process_tree: nDigraph, transition_label: str, show_graph: bool = True):
        edges = [e for e in process_tree.edges]
        ParserPCCGraph(transition_label, edges, 0, show_graph)
