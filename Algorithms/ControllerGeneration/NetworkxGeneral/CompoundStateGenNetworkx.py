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

from typing import Dict, Tuple, List, Union

from networkx import MultiDiGraph

from Algorithms.ControllerGeneration.NetworkxGeneral.TreeBaseNetworkx import TreeBaseNetworkx
from DataObjects.States.ClassCompoundState import CompoundState
from DataObjects.States.ClassStatev2 import State_v2


## CompoundStateGenNetworkx
#
#  Generate new compound states when graphs are interleaved or merged
class CompoundStateGenNetworkx(TreeBaseNetworkx):

    def __init__(self, prefix: str = ""):
        TreeBaseNetworkx.__init__(self)

        # Add a prefix to all new compound states, if these are neither root nor terminal states
        self.prefix = prefix
        # Track all states and their respective updates
        self.chain_state_dict: Dict[Tuple[State_v2, ...], CompoundState] = {}

    def clear_chain_state_dict(self):
        self.chain_state_dict: Dict[Tuple[State_v2, ...], CompoundState] = {}

    def gen_compound_states_graph(self, graph: MultiDiGraph,
                                  chain_states: Union[List[State_v2], Tuple[State_v2]]) -> MultiDiGraph:
        updated_graph = MultiDiGraph()
        root_node = self.get_root_node_by_attribute(graph)
        terminal_nodes = self.get_terminal_nodes_by_attribute(graph)

        for transition in self.get_transitions_from_graph(graph):
            new_trans = transition.deepcopy_trans()

            # Prefix
            root_prefix = ""
            if not transition.start_state == root_node:
                root_prefix = self.prefix

            new_trans.update_state(new_trans.start_state,
                                   self.gen_compound_state(new_trans.start_state, chain_states, root_prefix))
            # The update function updates the start and final state alike, no new final state needs to be generated
            if new_trans.start_state != new_trans.final_state:

                # Prefix
                terminal_prefix = ""
                if transition.final_state not in terminal_nodes:
                    terminal_prefix = self.prefix
                new_trans.update_state(new_trans.final_state,
                                       self.gen_compound_state(new_trans.final_state, chain_states, terminal_prefix))

            self.add_transition_to_graph(updated_graph, new_trans)

            # Update the root identifiers
            if transition.start_state == root_node:
                self.set_root_node_attribute(updated_graph, new_trans.start_state)

            if transition.final_state in terminal_nodes:
                self.set_terminal_nodes_attribute(updated_graph, new_trans.final_state)

        return updated_graph

    def gen_compound_state(self, state: State_v2, chain_states: List[State_v2], prefix: str) -> CompoundState:
        state_tuple = tuple([state] + list(chain_states))
        if state_tuple in self.chain_state_dict:
            return self.chain_state_dict[state_tuple]
        else:
            new_compound = CompoundState(state_tuple, prefix)
            self.chain_state_dict[state_tuple] = new_compound
            return new_compound
