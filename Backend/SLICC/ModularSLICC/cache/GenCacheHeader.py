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
from Backend.SLICC.ModularSLICC.common.GenMachineHeader import GenMachineHeader
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from Backend.SLICC.ModularSLICC.BackendOptions import OPTIONS, LLC_BANKED, LLC_RANGE


class GenCacheHeader(TemplateHandler):

    template_file = "cache_header.sm"
    template_file_2 = "cache_header_wL2.sm"
    def __init__(self, handler_dir: str):
        TemplateHandler.__init__(self, handler_dir)

    def gen_cache_header_str(self, arch: FlatArchitecture, id_mapping: dict[str, str]):
        const_str = "//" + __name__ + self.nl
        if len(id_mapping) > 2:
            header = GenMachineHeader.gen_machine_header_str(self, arch, id_mapping, GenCacheHeader.template_file, False)
            if OPTIONS.llc_mapping in (LLC_BANKED, LLC_RANGE):
                # LLC slices interleaved by address within the cluster (BackendOptions): the number of
                # selection bits and the cluster are configuration parameters, the low bit is the
                # block offset (banked) or the top of the physical address minus the selection bits
                # (range)
                llc = id_mapping[list(id_mapping.keys())[list(id_mapping.keys()).index(arch.arch_name) + 1]]
                header = header.replace(f"  int {llc}_id;{self.nl}",
                                        f"  int {llc}_id;{self.nl}  int l2_select_num_bits;{self.nl}"
                                        f"  int cluster_id;{self.nl}", 1)
                low_bit = "RubySystem::getBlockSizeBits()" if OPTIONS.llc_mapping == LLC_BANKED else \
                    "RubySystem::getRealPhysMemBits() - RubySystem::getL2Bits()"
                header = header.rstrip() + self.nl + \
                    f'  int l2_select_low_bit, default="{low_bit}";' + self.nl
            const_str += header
        else:
            const_str += GenMachineHeader.gen_machine_header_str(self, arch, id_mapping, GenCacheHeader.template_file_2, False)
        return const_str + self.nl
