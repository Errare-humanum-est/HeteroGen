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

import re
from typing import Dict, Tuple, Any
from collections import OrderedDict
from networkx import DiGraph

from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.ClassCluster import Cluster
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from Backend.SLICC.ModularSLICC.common import Util
from Backend.SLICC.ModularSLICC.common.GenMachineInPorts import GenMachineInPorts
from Backend.SLICC.ModularSLICC.common.GenSLICCTree import GenSLICCTree


class UniqueNode:

    def __init__(self, data: Any):
        self.data = data

    def __str__(self):
        return str(self.data)


class GenDirInPorts(TemplateHandler):

    def __init__(self, handler_dir: str):
        TemplateHandler.__init__(self, handler_dir)

    def gen_dir_in_ports_str(
            self,
            cluster: Cluster,
            arch: FlatArchitecture,
            in_ports: 'OrderedDict[str, str]',
            out_ports: 'OrderedDict[str, str]',
            machine_mappings: dict[str, str],
            main_memory_accesses: Dict[Tuple[str, str], DiGraph],
    ) -> str:

        fsm_in_ports = GenMachineInPorts.gen_machine_in_ports(
            self, cluster, arch, False, "Directory", in_ports, out_ports,
            machine_mappings, main_mem_accesses=main_memory_accesses)

        return "//" + __name__ \
               + self.nl \
               + self._gen_mem_in_port(cluster,
                                       arch,
                                       main_memory_accesses,
                                       Util.get_message_data_var(arch.global_arch),
                                       Util.get_active_cache_line(arch),
                                       out_ports,
                                       machine_mappings
                                       ) \
               + self.nl \
               + fsm_in_ports \
               + self.nl

    def _gen_mem_in_port(
            self,
            cluster: Cluster,
            arch: FlatArchitecture,
            main_mem_accesses: Dict[Tuple[str, str], DiGraph],
            message_data_var: str,
            cache_line: str,
            out_ports: 'OrderedDict[str, str]',
            machine_mappings: dict[str, str],
    ) -> str:

        slicc_tree_gen = GenSLICCTree(cluster, arch, False, "", out_ports, machine_mappings, allow_port_popping=False)
        body_strs = []
        for (state, mem_access), operation_tree in main_mem_accesses.items():

            end_nodes = [node for node, degree in operation_tree.out_degree(operation_tree.nodes) if degree == 0]
            for end_node in end_nodes:
                if "trigger(Event" not in operation_tree.nodes[end_node]['op_str']:
                    # Let's also try always executing a "dummy" event to force SLICC to progress...
                    dummy_str = Util.gen_progress_str(self, False)
                    dummy_node = UniqueNode(str(end_node) + dummy_str)
                    operation_tree.add_node(dummy_node, op_str=dummy_str)
                    operation_tree.add_edge(end_node, dummy_node)

            ops = slicc_tree_gen.tree_to_str(operation_tree)
            ops = re.sub(r"in_msg\.Sender", "in_msg.OriginalRequestorMachId", ops)
            # remove (now redundant) writes
            ops = re.sub(rf"^.*getEntry\(LineAddress\)\.{cache_line} :=.*$", "", ops, flags=re.MULTILINE)
            ops = re.sub(rf"in_msg\.{message_data_var}", "in_msg.DataBlk", ops)
            # gen_make reads refer to contents of memory reads instead
            ops = re.sub(rf":= getEntry\(LineAddress\)\.{cache_line};", ":= in_msg.DataBlk;", ops)

            body_strs.append(f"if (st == State:{state} {self.nl}{self.tab}{self.tab}{self.tab}"
                             f"&& in_msg.Type == MemoryRequestType:{mem_access}) {{{self.nl}"
                             f"{self.add_tabs(ops, 1)}{self.nl}}}"
                             )

        body = " else ".join(body_strs) \
               + f" else {{{self.nl}{self.tab}{Util.gen_stall_str(self, False, 'memQueue_in')}}}"

        return self.string_repl_keys(self.open_template("memory_in_port.sm"), [self.add_tabs(body, 3)])
