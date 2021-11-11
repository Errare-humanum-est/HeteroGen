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
from collections import Counter
import networkx as nx
from networkx import MultiDiGraph
import copy

from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from DataObjects.ClassMachine import Machine
from DataObjects.ClassMultiDict import MultiDict
from DataObjects.ClassSystemTuple import SystemTuple
from DataObjects.FlowDataTypes.ClassMessage import Message
from DataObjects.FlowDataTypes.ClassEvent import Event
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess

from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from Debug.Graphv.ParserNetworkxGraph import ParserPCCGraph
from Debug.Monitor.ClassDebug import Debug


class UUTMachine:
    def __init__(self, machine: Machine, mach_id: int):

        # Every machine gets an index, this index is used in ID and vectors and messages to identify the machine
        self.mach_id = mach_id
        # The machine contains the trace that needs to be executed
        self.machine = machine
        # The variable type definition
        self.local_var_types = machine.arch.machine.variables
        # The name of the architecture like for example "MSIcache" or "directory"
        self.mach_type_name = machine.arch.machine.mach_id


class UUT:
    def __init__(self, uut_machine: UUTMachine):

        # The uut machine description hold constant declarations
        # By passing a previously used UUT machine where the machine trace was changed, the variables can continued to
        # be used
        self.uut_machine = uut_machine

        # Index that tracks which transition of the trace is currently being executed
        self.trans_index = 0

        self.cur_transition = None
        self.trans_count = 0
        # Current transition being executed
        if self.uut_machine.machine.cur_trace:
            self.cur_transition = self.uut_machine.machine.cur_trace.trace_trans[self.trans_index]
            # Number of transitions
            self.trans_count = len(uut_machine.machine.cur_trace.trace_trans)

        # Initialize the variables
        self.local_vars: Dict[str, Union[int, str]] = {}
        # Track internal event, the event count must never exceed one as only per cache line trace checking is performed
        self.local_event = []

    def __str__(self):
        return str(self.cur_transition)

    # Checks if the machine wants to perform an access
    def check_access_uut_guard(self) -> bool:
        if not self.trans_index < self.trans_count:
            return False

        if isinstance(self.cur_transition.guard, BaseAccess.Access_type):
            return True
        return False

    # Checks if the passed Message or Event matches the guard
    def check_basic_uut_guard(self, guard: Union[Message, Event]) -> bool:
        if not self.trans_index < self.trans_count:
            return False

        if isinstance(guard, Message):
            # Only if local variables are set it makes sense to track the destinations of messages and to copy them to
            # modify their destination dynamically
            if not self.local_vars \
                    and str(guard) == str(self.cur_transition.guard):
                return True
        else:
            if self.local_event and guard == self.local_event[0]:
                return True

        return False

    def execute_uut(self) -> Tuple['UUT', List[Union[Message, Event]]]:
        # Make new UUT instance to be returned to system state
        new_uut = self.copy_uut()

        # Track the out_messages that are sent by the machine
        out_msg_list = []

        if self.cur_transition.out_event:
            new_uut.local_event = [self.cur_transition.out_event]
            # An event must be communicated to the system state, as the simulation stops if the pending message becomes
            # empty and to keep the simulation kernel more general
            out_msg_list.append(self.cur_transition.out_event)

        # Only if local variables are defined or initialized the communication pattern is analyzed in detail
        # Sharer handling is required to properly support multi casting behaviour
        if self.local_vars:
            pass
        else:
            out_msg_list += self.cur_transition.out_msg

        return new_uut, out_msg_list

    def process_operations(self, transition):
        # Only if local variables are set it makes sense to track the destinations of messages and to copy them to
        # modify their destination dynamically
        msg_copies = []

    def copy_uut(self) -> 'UUT':
        new_uut = copy.copy(self)
        # Increment transition index
        new_uut.trans_index += 1
        if new_uut.trans_index < self.trans_count:
           new_uut.cur_transition = self.uut_machine.machine.cur_trace.trace_trans[new_uut.trans_index]
        else:
            new_uut.cur_transition = None
        new_uut.local_event = []
        new_uut.local_vars = copy.copy(self.local_vars)

        return new_uut


class SystemState:
    def __init__(self, uut_list: List[UUT]):
        self.uut: List[UUT] = uut_list
        self.init_local_variables = False
        # The execution tick is the index of how many transitions have already been handled
        # The maximum number of the execution tick is the total number of transitions across all machines
        self.execution_tick = 0
        self.max_execution_tick = self.get_max_execution_tick()
        # If a UUT gets its own event passed it is serving this event
        self.pending_events_and_messages: List[Union[Message, Event]] = []
        # If message sources and destinations are not tracked in detail, then broadcast and multicast messages persist
        self.multicast_messages: List[Message] = []

    def get_max_execution_tick(self):
        max_execution_tick = 0
        for uut in self.uut:
            max_execution_tick += uut.trans_count
        return max_execution_tick

    def find_next_tuples(self) -> List[Tuple['SystemState', UUT]]:
        new_system_state: List[Tuple[SystemState, UUT]] = []

        # Terminal condition if maximum tick was reached
        if not self.execution_tick < self.max_execution_tick:
            return []

        for uut in self.uut:
            found = 0
            # Check if any of the ready guards can be executed
            for ready_guard in self.pending_events_and_messages + self.multicast_messages:
                if uut.check_basic_uut_guard(ready_guard):
                    # Returns the new system state and the served uut state
                    new_system_state.append((self.execute_next_tuple(uut, ready_guard), uut))
                    found = 1
                    break

            # Check if the uut can issue a new access transition
            if not found and uut.check_access_uut_guard():
                new_system_state.append((self.execute_next_tuple(uut, None), uut))

        return new_system_state

    def execute_next_tuple(self, uut: UUT, ready_guard: Union[Message, Event, None]):
        new_system_state = self.gen_new_system_state()
        new_uut, out_msg_list = uut.execute_uut()
        self.replace_uut(new_system_state, uut, new_uut)
        self.update_msgs(new_system_state, ready_guard, out_msg_list)

        return new_system_state

    def gen_new_system_state(self) -> 'SystemState':
        new_system_state = copy.copy(self)
        # Update the system state execution tick
        new_system_state.execution_tick += 1
        # Copy uut list
        new_system_state.uut = copy.copy(new_system_state.uut)
        # Copy pending message and multicast lists
        new_system_state.pending_events_and_messages = copy.copy(new_system_state.pending_events_and_messages)
        new_system_state.multicast_messages = copy.copy(new_system_state.multicast_messages)

        return new_system_state

    @staticmethod
    def replace_uut(new_system_state: 'SystemState', uut: UUT, new_uut: UUT):
        new_system_state.uut.remove(uut)
        new_system_state.uut.append(new_uut)

    @staticmethod
    def update_msgs(new_system_state: 'SystemState',
                    ready_guard: Union[Message, Event, None],
                    out_msg_list: List[Union[Message, Event]]):
        if ready_guard in new_system_state.pending_events_and_messages:
            new_system_state.pending_events_and_messages.remove(ready_guard)

        for out_msg in out_msg_list:
            if isinstance(out_msg, Event):
                new_system_state.pending_events_and_messages.append(out_msg)
            else:
                if (out_msg.msg_routing.cast in ProtoParserBase.kmbcast and
                        str(out_msg) not in [str(msg) for msg in new_system_state.multicast_messages]):
                    new_system_state.multicast_messages.append(out_msg)
                else:
                    new_system_state.pending_events_and_messages.append(out_msg)

    def trace_sanity_check(self):
        if not self.pending_events_and_messages and not self.execution_tick < self.max_execution_tick:
            return True
        return False


class TraceCheckerGraphNode:

    def __init__(self, system_state: SystemState, uut: Union[UUT, None]):
        self.system_state: SystemState = system_state
        self.uut: UUT = uut

    def __str__(self):
        if self.uut:
            return str(self.uut.cur_transition) + " | Tick-" + str(self.system_state.execution_tick) + '- | '
        else:
            return 'Tick-' + str(self.system_state.execution_tick) + '- | '


# Determines all possible execution sequences and interleaving of two traces
class TraceCheckGraph:

    def __init__(self, system_tuple: SystemTuple):
        self.mach_name_id_map: MultiDict = MultiDict()
        # All transitions that are expected to be served in the TraceCheckExecution
        self.machine_transitions_list: List[Transition_v2] = []

        # Initialize System tuple
        self.initial_system_state = self.gen_initial_system_state(system_tuple)

        self.exec_graph: MultiDiGraph = MultiDiGraph()
        self.initial_node = TraceCheckerGraphNode(self.initial_system_state, None)
        self.exec_graph.add_node(self.initial_node)

        self.run_trace_checker()

    def gen_initial_system_state(self, system_tuple: SystemTuple) -> SystemState:
        uut_list: List[UUT] = []
        for uut_machine in self.gen_uut_machines_from_system_tuple(system_tuple):
            uut_list.append(UUT(uut_machine))
            # Collect all transitions that need to be served in execution
            if uut_machine.machine.cur_trace:
                self.machine_transitions_list += uut_machine.machine.cur_trace.trace_trans
        return SystemState(uut_list)

    # Generate the UUTS from the system tuple
    def gen_uut_machines_from_system_tuple(self, system_tuple: SystemTuple) -> List[UUTMachine]:
        uut_machines: List[UUTMachine] = []
        for mach_id in range(0, len(system_tuple.system_tuple)):
            new_uut_machine = UUTMachine(system_tuple.system_tuple[mach_id], mach_id)
            uut_machines.append(new_uut_machine)
            self.mach_name_id_map[new_uut_machine.mach_type_name] = mach_id
        return uut_machines

    # Generate new trace
    def run_trace_checker(self):
        next_nodes: List[TraceCheckerGraphNode] = self.get_exec_graph_terminal_nodes()
        terminal_nodes: List[TraceCheckerGraphNode] = []

        while next_nodes:
            for next_node in next_nodes:
                if next_node in terminal_nodes:
                    continue

                # Execute system state and all ready unit under tests
                new_exec_tuples = next_node.system_state.find_next_tuples()

                # No new execution tuples found, so the execution has finished for this system state
                if not new_exec_tuples:
                    terminal_nodes.append(next_node)
                    continue

                # Add the new system tuples to the execution graph
                for new_exec_tuple in new_exec_tuples:
                    self.exec_graph.add_edge(next_node, TraceCheckerGraphNode(*new_exec_tuple))

            # Get the next nodes that are not terminal yet
            next_nodes = [node for node in self.get_exec_graph_terminal_nodes() if node not in terminal_nodes]

    def debug_trace_graph(self):
        ParserPCCGraph.debug_process_graph(self.exec_graph, "Dummy", True)

    def get_exec_graph_root_nodes(self) -> List[TraceCheckerGraphNode]:
        return self.exec_graph.successors(self.initial_node)

    def get_exec_graph_terminal_nodes(self) -> List[TraceCheckerGraphNode]:
        return list((node for node, out_degree in self.exec_graph.out_degree(self.exec_graph.nodes) if out_degree == 0))

    def get_trans_traces(self) -> Union[List[List[Transition_v2]], None]:
        node_paths = []
        for start_node in self.exec_graph.successors(self.initial_node):
            for term_node in self.get_exec_graph_terminal_nodes():
                if start_node != term_node:
                    node_paths += nx.all_simple_paths(self.exec_graph, start_node, term_node)
                else:
                    node_paths.append([start_node])

        trans_traces = []
        for node_path in node_paths:
            trans_traces.append([node.uut.cur_transition for node in node_path])

        #valid_traces = self.check_trace_completeness(trans_traces)
        #return valid_traces
        return self.check_trace_completeness(trans_traces)

    def check_trace_completeness(self, trans_traces: List[List[Transition_v2]]) -> \
            Union[List[List[Transition_v2]], None]:
        ref_counter = Counter(self.machine_transitions_list)
        for trans_trace in trans_traces:
            if ref_counter == Counter(trans_trace):
                return trans_traces
        return None

    def get_complete_traces(self, trans_traces: List[List[Transition_v2]]) -> List[List[Transition_v2]]:
        ref_counter = Counter(self.machine_transitions_list)
        valid_trans_traces = []
        for trans_trace in trans_traces:
            if ref_counter == Counter(trans_trace):
                valid_trans_traces.append(trans_trace)
            else:
                Debug.pwarning("Incomplete trace detected at trace checker: ")
                Debug.pwarning("Expected transition coverage: " + str(self.machine_transitions_list))
                Debug.pwarning("Actual transition covereage:  " + str(trans_trace))
                Debug.pwarning("Trace omitted")

        return valid_trans_traces
