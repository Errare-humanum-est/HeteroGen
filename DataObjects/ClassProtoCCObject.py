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

from typing import Dict

from Parser.ProtoCCParser import ProtoCCParser
from Parser.ProtoCCcomTreeFct import *
from Debug.Monitor.ClassDebug import Debug


class PCCObject:
    def __init__(self, node, debug_enable: bool = False):

        dbg = Debug(debug_enable)
        assert isinstance(node, CommonTree)

        self.structure = node

        definitions = node.getChildren()
        self.name = definitions[0].getText()
        self.variables = {}
        self.getvarnames(definitions)
        dbg.pdebug("Object: " + node.getText() + " " + self.name + " -> varNames: " + str(self.variables))

    def __str__(self):
        return self.name

    def getvarnames(self, nodes):
        self.variables = {}
        assign = 'INITVAL_'
        for node in nodes:
            # Check if data type
            if node.getText() in ProtoCCParser.tokenNames:
                entry = toStringList(node)
                if assign in entry:
                    self.variables.update({entry[entry.index(assign)-1]: node.getText()})
                else:
                    self.variables.update({entry[-1]: node.getText()})

    def get_var_object_dict(self) -> Dict[str, CommonTree]:
        nodes = self.structure.getChildren()
        var_obj_dict = {}
        assign = 'INITVAL_'
        for node in nodes:
            # Check if data type
            if node.getText() in ProtoCCParser.tokenNames:
                entry = toStringList(node)
                if assign in entry:
                    var_obj_dict.update({entry[entry.index(assign) - 1]: node})
                else:
                    var_obj_dict.update({entry[-1]: node})
        return var_obj_dict

    def getname(self):
        return self.name

    def getvariables(self):
        return self.variables

    def testname(self, name):
        if name == self.name:
            return 1
        return 0

    def testvariable(self, name):
        if name in self.variables:
            return 1
        return 0

    def getnode(self):
        return self.structure
