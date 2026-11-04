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
from Backend.SLICC.ModularSLICC.common import Util
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture


class GenMachineHeader:

    @staticmethod
    def gen_machine_header_str(temp_h: TemplateHandler, arch: FlatArchitecture, id_mapping: dict[str, str], template_file: str, flip_direction: bool) -> str:
        nets = []
        list(id_mapping.keys()).index(arch.arch_name)
        keys = list(id_mapping.keys())
        index = keys.index(arch.arch_name)
        machine_id = id_mapping[keys[index]]
        if index < len(keys) - 1:
            next_machine_id = id_mapping[keys[index + 1]]
        # Virtual networks are numbered in the declaration order of the (merged) networks, the same for
        # every machine; a machine declares the networks it uses only (Util.used_networks), each with
        # two buffers, one "to" and one "from" the network.
        used = Util.used_networks(arch)
        # Will have to worry about the ordering constraints when setting up the config file, not now
        for idx, net_name in enumerate(arch.global_arch.network.network_order):
            if used and net_name not in used:
                continue
            virtual_channel = str(idx)
            for direction in ("To", "From"):
                net_direction = direction if not flip_direction else Util.reverse_direction(direction)
                nets.append(temp_h.string_repl_keys(temp_h.open_template("message_buffer.sm"),
                                                    [net_name + direction,
                                                     net_direction,
                                                     virtual_channel,
                                                     net_name
                                                     ]
                                                    )
                            )

        nets_str = (temp_h.nl + temp_h.tab).join(nets)
        if index < len(keys) - 2:
            return temp_h.string_repl_keys(temp_h.open_template(template_file), [machine_id, next_machine_id, nets_str])
        else:
            return temp_h.string_repl_keys(temp_h.open_template(template_file), [machine_id, nets_str])
