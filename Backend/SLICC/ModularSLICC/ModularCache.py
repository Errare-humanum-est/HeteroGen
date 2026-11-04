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

from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.ClassCluster import Cluster
from Backend.SLICC.ModularSLICC.common import Util
from Backend.SLICC.ModularSLICC.cache.GenCacheBase import GenCacheBase


class ModularCache(GenCacheBase):
    TemplateDir = "TempSLICC/machines"

    def __init__(self, cluster: Cluster, arch: FlatArchitecture, file_name: str):
        GenCacheBase.__init__(self, self.TemplateDir)

        file_name = file_name.split(".")[0] + "_cache.sm"

        out_ports = Util.get_out_ports(arch)
        in_ports = Util.get_in_ports(arch)

        with open(file_name, "w") as slicc_file:
            # Write header
            slicc_file.write(self.gen_cache_header_str(arch))
            # Write (indented) body
            slicc_file.write(
                self.add_tabs(
                    ''.join([self.gen_cache_state_decl_str(arch) + self.nl,
                             self.gen_cache_events_str(arch, in_ports) + self.nl,
                             self.gen_cache_struct_str(arch) + self.nl,
                             self.gen_cache_tbe_str(arch) + self.nl,
                             self.gen_cache_static_fns_str(arch) + self.nl,
                             self.gen_cache_out_ports_str(out_ports) + self.nl,
                             self.gen_cache_in_ports_str(cluster, arch, in_ports, out_ports) + self.nl,
                             self.gen_cache_actions_str(cluster, arch, in_ports, out_ports) + self.nl,
                             self.gen_cache_transitions_str(arch, in_ports),
                             ]
                            ),
                    1
                )
                + self.nl
            )
            # Write footer / close the controller
            slicc_file.write(self.gen_cache_footer_str())
