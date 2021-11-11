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

from typing import List, Dict, Set

from networkx import MultiDiGraph, is_strongly_connected

from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.States.ClassStatev2 import State_v2
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from Parser.ProtoCCcomTreeFct import toStringList
from Debug.Monitor.ClassDebug import Debug
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess

from Debug.Graphv.ProtoCCGraph import ProtoCCGraph


## GraphCheck
#
#  Performs multiple sanity checks for the graph
#  Dependency: ProtoParserBase, Debug
class GraphCheck(BaseAccess, Debug):

    def __init__(self, transitions: List[Transition_v2]):
        Debug.__init__(self)

        networkx_graph = self.gen_multidigraph_from_transitions(transitions)

        # First check for terminal states
        self.terminal_state_check(networkx_graph, transitions)

        # Second check for non_reachable states
        self.is_reachable_state_check(networkx_graph, transitions)

        # Check if all states are connected
        self.is_connected_node_check(networkx_graph, transitions)

        # Check that every stable state has transitions with unique guards and conditions
        self.guard_cond_check(transitions)

    def get_cond_operation(self, transition: Transition_v2) -> Set[str]:
        cond_set: Set[str] = set()
        for operation in transition.operations:
            if str(operation) in ProtoParserBase.CondKeys:
                cond_set.add(tuple(toStringList(operation)))
        return cond_set

    # Check that for every state no guard and condition combination occurs twice
    def guard_cond_check(self, transitions: List[Transition_v2]):
        state_operation_dict: Dict[State_v2, Set[str]] = {}
        for transition in transitions:
            guard_cond_set = self.get_cond_operation(transition)
            guard_cond_set.add(str(transition.guard))

            if transition.start_state not in state_operation_dict or \
                    guard_cond_set not in state_operation_dict[transition.start_state]:
                state_operation_dict[transition.start_state] = guard_cond_set
            else:
                self.perror("In State: " + str(transition.start_state) + "the following guard, "
                                                                         "condition combination was found twice in "
                                                                         "different transitions: "
                            + str(guard_cond_set))

    # Checks if all nodes are connected and reachable from any other node
    def is_connected_node_check(self, trans_graph: MultiDiGraph, transitions: List[Transition_v2]):
        start_states = set([trans.start_state for trans in transitions])
        Debug.perror("No states found", len(start_states) > 0)

        # A graph with one node has no connectivity issues
        if len(start_states) == 1:
            return

        is_connected_bool: bool = is_strongly_connected(trans_graph)

        if not is_connected_bool:
            ProtoCCGraph("Unconnected graphs found", transitions)

        self.perror("Unconnected graphs found", is_connected_bool)

    def is_reachable_state_check(self, trans_graph: MultiDiGraph, transitions: List[Transition_v2]):
        non_reachable_states = [x for x in trans_graph.nodes()
                                if trans_graph.out_degree(x)==1 and trans_graph.in_degree(x)==0]

        if non_reachable_states:
            ProtoCCGraph("Non reachable states found: " + str(non_reachable_states), transitions)

        self.perror("Non reachable states found: " + str(non_reachable_states), not non_reachable_states)

    # Check if a terminal state exists in the graph
    def terminal_state_check(self, trans_graph: MultiDiGraph, transitions: List[Transition_v2]):
        terminal_states = [x for x in trans_graph.nodes()
                           if trans_graph.out_degree(x)==0 and trans_graph.in_degree(x)==1]

        if terminal_states:
            ProtoCCGraph("Terminal states found: " + str(terminal_states), transitions)

        self.perror("Terminal states found: " + str(terminal_states), not terminal_states)

    def gen_multidigraph_from_transitions(self, transitions: List[Transition_v2]) -> MultiDiGraph:
        trans_graph: MultiDiGraph = MultiDiGraph()

        for transition in transitions:
            if str(transition.start_state) != str(transition.final_state):
                trans_graph.add_edge(str(transition.start_state), str(transition.final_state))

        return trans_graph
