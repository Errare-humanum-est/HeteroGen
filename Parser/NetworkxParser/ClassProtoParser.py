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

import antlr3

from antlr3.tree import CommonTree
from collections import OrderedDict
from typing import Dict, Union, List, Set

from Debug.Monitor.ClassDebug import Debug
from Debug.Monitor.ProtoCCTable import ProtoCCTablePrinter

from Parser.ProtoCCLexer import ProtoCCLexer
from Parser.ProtoCCParser import ProtoCCParser
from Parser.CopyReducedCommonTree import copy_tree

from Parser.DataTypes.ClassConstants import Constants
from Parser.DataTypes.ClassBaseNetwork import BaseNetwork, BaseMessage
from Parser.DataTypes.ClassGuard import Guard

from Debug.Graphv.ProtoCCGraph import ProtoCCGraph
from DataObjects.FlowDataTypes.ClassBaseAccess import BaseAccess
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2

from Parser.DataTypes.ClassProtoMachine import ProtoMachine
from Parser.NetworkxParser.ClassProtoArchitecture import SSPArchitecture
from DataObjects.Architecture.ClassGlobalBaseArchitecture import GlobalBaseArchitecture
from Debug.Monitor.MakeDir import make_dir, dir_up


class ProtoParser(Debug):

    # PARSER TOKENS ####################################################################################################
    Objects = {
        'CONSTANT_': '_CreateConstant',
        'NETWORK_': '_CreateNetwork',
        'CACHE_': '_CreateCache',
        'DIR_': '_CreateDir',
        'MEM_': '_CreateMem',
        'MSG_': '_CreateMsgObj',
        'ARCH_': '_CreateArch',
    }

    # Keywords
    Data = 'DATA_'
    State = 'State'

    def __init__(self, file="", filename="", graph_export: bool = False, dbg_enabled: bool = False):
        Debug.__init__(self, dbg_enabled)

        # Change the output directory for the graph
        make_dir("ParserOutput")

        # PROTO DATA OBJECTS ####
        self.filename = filename
        self.constants: Constants = Constants()

        # Architecture nodes
        self.cache_node: ProtoMachine = None
        self.dir_node: ProtoMachine = None
        self.mem_node: ProtoMachine = None
        self.machines: Dict[str, ProtoMachine] = {}

        self.base_access: BaseAccess = BaseAccess()
        self.base_network: BaseNetwork = BaseNetwork()

        self.architectures: Dict[str, SSPArchitecture] = {}
        self.global_arch: GlobalBaseArchitecture = GlobalBaseArchitecture()
        self.global_arch.base_access = self.base_access
        self.global_arch.network = self.base_network
        self.global_arch.constants = self.constants

        if file and filename:
            # Parse the input file
            lexer = ProtoCCLexer(antlr3.StringStream(file))
            parser = ProtoCCParser(antlr3.CommonTokenStream(lexer))

            # Copy the tree
            tree = parser.document().getTree()
            new_tree_base = copy_tree(tree)

            self.pdebug(new_tree_base.toStringTree())
            self._ParseNodes(new_tree_base)

            self._update_guards()

            # Print graphs to output
            self._pArchTable()

            if graph_export:
                self._dArch()

        # Return to parent working directory
        dir_up()

    def get_cache_architecture(self) -> SSPArchitecture:
        return self.architectures[str(self.cache_node)]

    def get_dir_architecture(self) -> Union[SSPArchitecture, None]:
        if self.dir_node:
            return self.architectures[str(self.dir_node)]
        return None

    def get_mem_architecture(self) -> Union[SSPArchitecture, None]:
        if self.mem_node:
            return self.architectures[str(self.mem_node)]
        return None

########################################################################################################################
# PARSER ENTRY POINT
########################################################################################################################

    def _ParseNodes(self, tree):
        objects = tree.getChildren()
        for obj in objects:
            method_fct = self.Objects[obj.getText()]
            method = getattr(self, method_fct, lambda: '__UnknownNode__')
            method(obj)

    def _UnknownNode(self, obj):
        self.perror("Unknown Node Identifier")
        self.perror(obj.getText())

########################################################################################################################
# SECTIONS
########################################################################################################################

    def _CreateConstant(self, obj: CommonTree):
        self.constants.add_const(obj)

    def _CreateNetwork(self, obj: CommonTree):
        self.base_network.gen_virtual_channels(obj)

    def _CreateCache(self, obj: CommonTree):
        assert not self.cache_node, "A cache has already been defined at this level"
        self.cache_node = ProtoMachine(obj, self.constants)
        self.machines[str(self.cache_node)] = self.cache_node

    def _CreateDir(self, obj: CommonTree):
        assert not self.dir_node, "A directory has already been defined for this level"
        self.dir_node = ProtoMachine(obj, self.constants)
        self.machines[str(self.dir_node)] = self.dir_node

    def _CreateMem(self, obj: CommonTree):
        assert not self.mem_node, "A memory has already been defined for this level"
        self.mem_node = ProtoMachine(obj, self.constants)
        self.machines[str(self.mem_node)] = self.mem_node

    def _CreateMsgObj(self, obj: CommonTree):
        self.base_network.gen_msg_type(obj)

    def _CreateArch(self, arch_node: CommonTree):
        self.machine_node = self.machines[str(arch_node.getChildren()[0].getChildren()[0])]

        self.architectures[str(self.machine_node)] = \
            SSPArchitecture(arch_node, self.machine_node, self.global_arch, False)

        self.pdebug("Architecture " + str(self.machine_node) + ", #Transitions: " +
                    str(len(self.architectures[str(self.machine_node)].get_architecture_transitions())))

    def _update_guards(self):
        for arch in self.architectures:
            for transition in self.architectures[arch].get_architecture_transitions():
                if not isinstance(transition.guard, Guard):
                    continue
                if str(transition.guard) in self.base_network.base_message_dict:
                    if len(self.base_network.base_message_dict[str(transition.guard)]) > 1:
                        self.pwarning("Multiple message types defined for identifier: " + str(transition.guard) +
                                      " automatic assignment not possible, be careful with model checker output")
                        # What can be done to gen_make a decision is to parse through the operations and check which
                        # variables are used
                        transition.guard = self._find_minimal_message_type(transition)
                    else:
                        transition.guard = self.base_network.base_message_dict[str(transition.guard)][0]
                elif str(transition.guard) in self.base_access.access_map:
                    transition.guard = self.base_access.access_map[str(transition.guard)]
                else:
                    self.pwarning("Transition guard type unknown, doesn't seem to be a message, " +
                                  "event, as default it is interpreted as custom access?: " + str(transition))
                    transition.guard = self.base_access.map_access_to_base_access(str(transition.guard), None)

            # Update is required as the traces might have changed
            self.architectures[arch].update_base_fsm(self.architectures[arch].init_state,
                                                     self.architectures[arch].stable_states,
                                                     self.architectures[arch].get_architecture_transitions())


    ## The network messages and internal events must not have identical names. Otherwise they cannot be distinguished
    #
    def _network_event_guard_sanity_check(self):
        pass

    def _find_minimal_message_type(self, transition: Transition_v2) -> BaseMessage:
        msg_var_dict = self._message_variable_set(str(transition.guard))
        op_var_set = self._extract_guard_variabels(transition)

        for msg_var_tuple in msg_var_dict:
            if op_var_set.issubset(set(msg_var_tuple)):
                return msg_var_dict[msg_var_tuple]

        self.perror("No matching message type could automatically be found for guard of transition: " + str(transition))

    def _message_variable_set(self, msg_id: str):
        var_dict = OrderedDict()
        for base_msg in self.base_network.base_message_dict[msg_id]:
            var_dict[tuple(base_msg.msg_type.msg_vars.keys())] = base_msg
        # Sort list by the number of variables
        return OrderedDict(sorted(var_dict.items(), key=lambda entry: len(entry[0])))

    def _extract_guard_variabels(self, transition: Transition_v2) -> Set:
        var_list = []
        for operation in transition.operations:
            self._seach_operations(var_list, str(transition.guard), operation)
        return set(var_list)

    def _seach_operations(self, var_list: List[str], msg_id: str, operation: CommonTree):
        for child in operation.getChildren():
            if str(child) == msg_id:
                self._extract_var(var_list, child)
            self._seach_operations(var_list, msg_id, child)

    def _extract_var(self, var_list: List[str], operation: CommonTree):
        children = operation.getChildren()
        if children and str(children[1]) not in [self.base_network.k_src, self.base_network.k_dst]:
            var_list.append(str(children[1]))


########################################################################################################################
# DEBUG
########################################################################################################################

    def _dArch(self):
        for arch in self.architectures:
            ProtoCCGraph("SSP_Spec: " + arch, list(self.architectures[arch].get_architecture_transitions()))

    def _pArchTable(self):
        for arch in self.machines:
            ProtoCCTablePrinter().ptransitiontable(list(self.architectures[arch].get_architecture_transitions()))

