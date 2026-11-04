#  Copyright (c) 2022.  Nicolai Oswald
#  Copyright (c) 2022.  University of Edinburgh
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
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler


class GenMachineActions:

    @staticmethod
    def gen_empty_action(temp_h: TemplateHandler) -> str:
        return temp_h.open_template("action_empty.sm")

    @staticmethod
    def gen_recycle_action(temp_h: TemplateHandler, port_name: str, shorthand: str) -> str:
        return temp_h.string_repl_keys(temp_h.open_template("action_recycle_port.sm"), [port_name, shorthand])

    @staticmethod
    def gen_pop_action(temp_h: TemplateHandler, port_name: str, shorthand: str) -> str:
        return temp_h.string_repl_keys(temp_h.open_template("action_pop_queue.sm"), [port_name, shorthand])

    @staticmethod
    def get_operation_action_name(start_state: str, end_state: str) -> str:
        return f"action{start_state}_{end_state}"

    @staticmethod
    def get_queue_pop_action_name(port_name: str) -> str:
        # Must match action_recycle_port.sm template
        return f"pop{port_name}"

