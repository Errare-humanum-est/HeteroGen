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

from typing import List, Dict, Union

from DataObjects.ClassCluster import Cluster

from Backend.Common.TemplateHandler.TemplateBase import TemplateBase
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens


class GenMachineSets(TemplateBase):

    def __init__(self, murphi_str: List[str], clusters: List[Cluster]):
        TemplateBase.__init__(self)

        mach_list: List[str] = []
        cluster_str = ""

        for cluster in clusters:
            cluster_str += "-- Cluster: " + str(cluster) + self.nl
            mach_cnt_dict = self.gen_cluster_machines(cluster)
            cluster_str += self.gen_obj_sets(mach_cnt_dict)
            cluster_str += self.gen_cluster_set(cluster, list(mach_cnt_dict.keys()))
            mach_list += list(mach_cnt_dict.keys())

        cluster_str += self.nl
        cluster_str += self.gen_mach_set(mach_list)

        cluster_str = "----" + __name__.replace('.','/') + self.nl + self.add_tabs(cluster_str, 1) + self.nl

        murphi_str.append(cluster_str)

    @staticmethod
    def gen_cluster_machines(cluster: Cluster) -> Dict[str, Union[int, str]]:
        mach_cnt_dict: Dict[str, Union[int, str]] = {}
        for arch in cluster.get_machine_architectures():
            mach_count = cluster.get_machine_architecture_count(arch)
            mach_cnt_dict[str(arch)] = mach_count
        return mach_cnt_dict

    def gen_obj_sets(self, mach_cnt_dict: Dict[str, int]):
        mach_set_str = ""
        for mach in mach_cnt_dict:
            mach_set_str += MurphiTokens.k_obj_set + mach + ": "
            if mach_cnt_dict[mach] > 1:
                mach_set_str += "scalarset(" + str(mach_cnt_dict[mach]) + ")" + self.end
            else:
                mach_set_str += "enum{" + str(mach) + "}" + self.end
        return mach_set_str

    def gen_cluster_set(self, cluster: Cluster, mach_cnt_dict: List[str]) -> str:
        cluster_set_str = str(cluster) + MurphiTokens.k_machines + ": union{"
        for mach in mach_cnt_dict:
            cluster_set_str += MurphiTokens.k_obj_set + str(mach) + ", "

        cluster_set_str = cluster_set_str[:cluster_set_str.rfind(",")]
        return cluster_set_str + "}" + self.end

    def gen_mach_set(self, mach_list: List[str]):
        mach_set_str = MurphiTokens.k_machines + ": union{"
        for mach in mach_list:
            mach_set_str += MurphiTokens.k_obj_set + str(mach) + ", "

        mach_set_str = mach_set_str[:mach_set_str.rfind(",")]
        return mach_set_str + "}" + self.end
