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

from DataObjects.ClassCluster import Cluster
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from Backend.SLICC.ModularSLICC.common import Util
from Backend.SLICC.ModularSLICC.dir.GenDirBase import GenDirBase


class ModularDir(GenDirBase):
    TemplateDir = "TempSLICC/machines"

    def __init__(self, cluster: Cluster, arch: FlatArchitecture, file_name: str, machine_mappings: dict[str, str]):
        GenDirBase.__init__(self, self.TemplateDir)

        file_name = file_name.split(".")[0] + "_dir_synth.sm"

        out_ports = Util.get_out_ports(arch, False)
        in_ports = Util.get_in_ports(arch, False)

        # In the directory we sometimes need to add an extra step in some transitions,
        # since the ProtoGen DSL does not explicitly deal with main memory but this is
        # required in gem5/SLICC. Dealing with this requires generating some new states
        # and then matching against those states in the main memory in_port.
        # Since this is only discovered when generating the in_ports, we need to do
        # this first even though we want them ordered last...
        # TODO this should be refactored to be handled more elegantly
        main_memory_accesses = {}
        dir_in_ports_str = self.gen_dir_in_ports_str(cluster, arch, in_ports, out_ports, machine_mappings, main_memory_accesses)

        with open(file_name, "w") as slicc_file:
            # Write header
            slicc_file.write(self.gen_dir_header_str(arch, machine_mappings))
            # Write (indented) body
            slicc_file.write(
                self.add_tabs(
                    ''.join([self.gen_dir_state_decl_str(arch, [key[0] for key in main_memory_accesses]) + self.nl,
                             self.gen_dir_events_str(in_ports) + self.nl,
                             self.gen_dir_struct_str(arch) + self.nl,
                             self.gen_dir_tbe_str() + self.nl,
                             self.gen_dir_static_fns_str(arch) + self.nl,
                             self.gen_dir_out_ports_str(out_ports) + self.nl,
                             dir_in_ports_str + self.nl,
                             self.gen_dir_actions_str(in_ports) + self.nl,
                             self.gen_dir_transitions_str(arch, [key[0] for key in main_memory_accesses], in_ports),
                             ]
                            ),
                    1
                )
            )
            # Write footer / close the controller
            slicc_file.write(self.gen_dir_footer_str())
