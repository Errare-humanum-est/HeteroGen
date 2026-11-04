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

import os
from time import sleep

from DataObjects.ClassCluster import Cluster
from Debug.Monitor.MakeDir import make_dir
from Backend.SLICC.ModularSLICC.ModularMsg import ModularMsg
from Backend.SLICC.ModularSLICC.ModularDir import ModularDir
from Backend.SLICC.ModularSLICC.ModularCache import ModularCache

from Debug.Monitor.ClassDebug import Debug

sleep(0.05)


def RunSLICCModular(cluster: Cluster, file_name: str) -> None:
    path = os.getcwd()

    make_dir("SLICC")

    ModularMsg(cluster, file_name)

    file_name = "SLICC_TEST"

    # There must not exist more than one directory
    dir_list = []
    for arch in cluster.get_machine_architectures():
        if arch.machine.check_dir():
            ModularDir(cluster, arch, file_name)

    Debug.p_warning("More than one directory found, count is: " + str(len(dir_list)), len(dir_list) > 1)

    for arch in cluster.get_machine_architectures():
        if arch.machine.check_cache():
            ModularCache(cluster, arch, file_name)

    print("SLICC files were generated in: " + os.getcwd())

    os.chdir(path)

