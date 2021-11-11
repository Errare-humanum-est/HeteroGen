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

from antlr3.tree import CommonToken, CommonTree
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase


class BaseDeferMessage:

    def __init__(self):
        # Get global variables
        pass

    ## Generate pcc grammar compatible assignments to defer the messages
    @staticmethod
    def push_defer_message(defer_token: str, guard: str) -> CommonTree:
        new_operation = CommonTree(CommonToken(text=ProtoParserBase.k_assign))

        # Left side assignment
        new_operation.addChild(CommonTree(CommonToken(text=defer_token)))
        # Assignment operator
        new_operation.addChild(CommonTree(CommonToken(text="=")))
        # Right side assignment
        new_operation.addChild(CommonTree(CommonToken(text=str(guard))))
        return new_operation

    @staticmethod
    def pop_defer_message(defer_token: str, var_token: str, guard: str) -> CommonTree:
        new_operation = CommonTree(CommonToken(text=ProtoParserBase.k_assign))

        # Left side assignment
        new_operation.addChild(CommonTree(CommonToken(text=var_token + str(guard))))
        # Assignment operator
        new_operation.addChild(CommonTree(CommonToken(text="=")))
        # Right side assignment
        new_operation.addChild(CommonTree(CommonToken(text=str(defer_token + str(guard)))))
        return new_operation

