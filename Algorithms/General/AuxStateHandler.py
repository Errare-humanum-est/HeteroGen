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
#

from antlr3.tree import CommonTree
from typing import List, Dict

from Parser.ProtoCCcomTreeFct import toStringList
from Parser.CopyReducedCommonTree import copy_tree
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase


class AuxStateHandler:
    def __init__(self):
        pass

    ####################################################################################################################
    # Operation mutation
    ####################################################################################################################
    @staticmethod
    def cond_operations_var_rename(operations: List[CommonTree], var_name: str, new_var_name: str,
                                   terminal_token_names: List[str] = None) -> List[CommonTree]:
        if not terminal_token_names:
            terminal_token_names = []

        for ind in range(0, len(operations)):
            operation = operations[ind]
            token_list = toStringList(operation)
            if var_name in token_list:
                operations[ind] = AuxStateHandler.cond_rename_operation(operation,
                                                                        var_name,
                                                                        new_var_name,
                                                                        terminal_token_names)
        return operations

    @staticmethod
    def cond_rename_operation(operation: CommonTree, var_name: str, new_var_name: str,
                              terminal_token_names: List[str] = None):
        if not terminal_token_names:
            terminal_token_names = []

        new_operation = copy_tree(operation)
        nodes = AuxStateHandler.cond_extract_nodes(new_operation, terminal_token_names)

        for node in nodes:
            if node.getText() == var_name:
                node.token.text = new_var_name

        return new_operation

    @staticmethod
    def cond_extract_nodes(operation: CommonTree, terminal_token_names: List[str]):
        nodes = [operation]
        if not operation.children:
            return nodes

        for child in operation.children:
            if str(child) in terminal_token_names:
                continue
            tmp_nodes = AuxStateHandler.cond_extract_nodes(child, terminal_token_names)
            if isinstance(tmp_nodes, list):
                nodes += tmp_nodes
            else:
                nodes.append(tmp_nodes)

        return nodes

    @ staticmethod
    def save_rename_var(operations: List[CommonTree],
                        start_operation: CommonTree,
                        var_name: str,
                        new_var_name: str):
        start = 0
        for ind in range(0, len(operations)):
            operation = operations[ind]
            if operation == start_operation:
                start = 1
            elif start == 1:
                # Check for message var_name reassignment
                if operation.getText() == ProtoParserBase.k_assign:
                    if operation.getChildren()[0].getText() == var_name:
                        return

            # The initial variable assignment has been found
            if start == 1:
                operations[ind] = AuxStateHandler.cond_rename_operation(operation, var_name, new_var_name, [])
