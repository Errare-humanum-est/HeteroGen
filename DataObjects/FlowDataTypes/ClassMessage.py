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

from antlr3.tree import CommonTree
from Parser.DataTypes.ClassBaseNetwork import BaseMessage
from Parser.DataTypes.ClassBaseNetwork import Channel
from Parser.DataTypes.ClassBaseNetwork import MsgType

from Debug.Monitor.ClassDebug import Debug


class MsgRouting(Debug):
    def __init__(self, src: str = "", dest: str = "", cast: str = ""):
        Debug.__init__(self)
        self.src: str = src
        self.dest: str = dest
        self.cast: str = cast

    def __eq__(self, other):
        self.perror("Passed object is not of type MsgRouting", isinstance(other, MsgRouting))

        return self.src == other.src and self.dest == other.dest and self.cast == other.cast


class Message(Debug):
    def __init__(self,
                 base_msg: BaseMessage,
                 msg_object: CommonTree,
                 msg_routing: MsgRouting):
        Debug.__init__(self)

        self.base_msg: BaseMessage = base_msg

        self.msg_routing: MsgRouting = msg_routing

        self.msg_object: CommonTree = msg_object

        # Register message with base message to link dependency
        self.base_msg.register_message_object(self)

    def __str__(self):
        return str(self.base_msg.id)

    def __hash__(self):
        return hash(self.base_msg.id)

    # Base_msg object is mutable, hence get functions
    def get_id(self) -> str:
        return str(self)

    def get_src(self) -> str:
        return self.msg_routing.src

    def get_dest(self) -> str:
        return self.msg_routing.dest

    def get_msg_type(self) -> MsgType:
        return self.base_msg.msg_type

    def get_vc(self) -> Channel:
        return self.base_msg.vc

    def has_data(self) -> bool:
        return self.base_msg.has_data()

    def __eq__(self, other):
        if not isinstance(other, (BaseMessage, Message)):
            return False

        return self.base_msg == other.base_msg and self.msg_routing == other.msg_routing
