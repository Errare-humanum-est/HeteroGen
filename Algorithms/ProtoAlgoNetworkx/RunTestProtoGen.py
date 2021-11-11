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

import os
from typing import Union, List

from Algorithms.ProtoAlgoNetworkx.RunProtoGenNetworkx import RunProtoGenNetworkx
from Algorithms.ControllerGeneration.ProxyDirController.ClassProxyDirArchitecture import ProxyDirArchitecture

from DataObjects.ClassMachine import Machine
from DataObjects.ClassCluster import Cluster

from MurphiLitmusTests.ClassLitmusTest import LitmusTest
from MurphiLitmusTests.ClassThreadMapLitmusTest import MachThreadMapLitmusTest
from Backend.Murphi.RunMurphiModular import RunMurphiCheck

from Debug.Monitor.MakeDir import make_dir
from Debug.Monitor.ClassDebug import Debug


class RunTestProtoGen(Debug):

    def __init__(self, default_system_model: bool = False):
        Debug.__init__(self, True)
        self.default_system_model = default_system_model

    def run_test(self, file_name: str, path: str, litmus_test_list: Union[LitmusTest, List[LitmusTest], None] = None):
        if isinstance(litmus_test_list, LitmusTest):
            litmus_test_list = [litmus_test_list]

        os.chdir(path)
        file = open(file_name).read()
        make_dir("FlatGen")
        make_dir(file_name.split(".")[0])

        level = RunProtoGenNetworkx(file, file_name)

        proxy_dir_controller = ProxyDirArchitecture(level)
        level.directory = proxy_dir_controller

        # Deadlock testing
        cache_machine = Machine(level.cache)
        directory_machine = Machine(level.directory)
        cluster_1 = Cluster((cache_machine, cache_machine, cache_machine, directory_machine), 'C1')
        self.check_deadlock_freedom(file_name, cluster_1)
        #RunSLICCModular(cluster_1, file_name)

        if litmus_test_list:
            self.run_litmus_test(file_name, litmus_test_list, cache_machine, directory_machine)

    @staticmethod
    def check_deadlock_freedom(file_name: str, cluster: Cluster):
        RunMurphiCheck([cluster], file_name, None, 2000)

    @staticmethod
    def run_litmus_test(file_name: str, litmus_test_list: List[LitmusTest], cache_mach: Machine, dir_mach: Machine):
        for litmus_test in litmus_test_list:
            cache_thread_tuple = \
                tuple((cache_mach, litmus_test.threads[ind])for ind in range(0, len(litmus_test.threads)))
            cluster_1 = Cluster(tuple(ct_tuple[0] for ct_tuple in cache_thread_tuple) + tuple([dir_mach]), 'C1', False)

            mach_litmus_test = MachThreadMapLitmusTest(litmus_test.test_name, litmus_test.exists)
            for ct_tuple in cache_thread_tuple:
                mach_litmus_test.add_cache_mach_thread_map(*ct_tuple)

            RunMurphiCheck([cluster_1], file_name, mach_litmus_test, 500)

            print("NEXT LITMUS TEST")
