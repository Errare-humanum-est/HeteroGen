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
import re
import subprocess
from typing import List, Union

from DataObjects.ClassCluster import Cluster
from MurphiLitmusTests.ClassThreadMapLitmusTest import MachThreadMapLitmusTest

from Backend.Murphi.MurphiModular.Constants.GenConst import GenConst
from Backend.Murphi.MurphiModular.GenTypes import GenTypes
from Backend.Murphi.MurphiModular.GenVars import GenVars
from Backend.Murphi.MurphiModular.GenFunctions import GenFunctions
from Backend.Murphi.MurphiModular.GenStateMachines import GenStateMachines
from Backend.Murphi.MurphiModular.GenResetFunc import GenResetFunc
from Backend.Murphi.MurphiModular.GenRules import GenRules
from Backend.Murphi.MurphiModular.GenStartStates import GenStartStates
from Backend.Murphi.MurphiModular.GenInvariant import GenInvariant
from Backend.Murphi.BaseConfig import BaseConfig
from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates

from Debug.Monitor.ClassDebug import Debug


class ModularMurphi(TemplateHandler, Debug):

    murphi_path = '/home/tux/Desktop/murphi'

    def __init__(self, clusters: List[Cluster],
                 file_name: str,
                 verify_ssp: bool,
                 litmus_test: Union[MachThreadMapLitmusTest, None] = "",
                 base_config: BaseConfig = None):
        TemplateHandler.__init__(self)
        Debug.__init__(self)
        """ The following keywords need to be instance-specific. If they
            are not then verifying multiple protocols within one process
            (for example SSP + ProtoGen output) will lead to syntax errors
            in all but the very first of the generated Murphi files."""

        self.base_config = base_config
        if not base_config:
            self.base_config = BaseConfig(clusters, litmus_test)

        self.name = file_name.split('.')[0]
        self.clusters = clusters

        self.file_name = file_name.split(".")[0]
        if litmus_test:
            self.file_name = (self.file_name + '_' + litmus_test.test_name)

        murphi_out: List[str] = []

        self.gen_concurrent_murphi(murphi_out)
        self.safe_to_file("".join(murphi_out))

########################################################################################################################
# RUN MURPHI
########################################################################################################################
    def gen_concurrent_murphi(self, murphi_out: List[str]):
        # Generate the constants
        GenConst(murphi_out, self.clusters, self.base_config)
        # Generate the enums (Access, MsgType, States, Machine objects)
        GenTypes(murphi_out, self.clusters, self.base_config)
        # Generate the variables
        GenVars(murphi_out, self.clusters, self.base_config)
        # Generate the general functions
        GenFunctions(murphi_out, self.clusters, self.base_config)
        # Generate the state machines
        GenStateMachines(murphi_out, self.clusters, self.base_config)
        # Generate the global reset function
        GenResetFunc(murphi_out, self.clusters, self.base_config)
        # Generate the network ruleset
        GenRules(murphi_out, self.clusters, self.base_config)
        # Generate the initial state by calling the reset function
        GenStartStates(murphi_out)
        # Generate the invariants
        GenInvariant(murphi_out, self.base_config)

    def safe_to_file(self, murphi_str: str):
        file_name = self.file_name.split(".")[0] + ".m"
        murphifile = open(file_name, "w")
        print("Murphi model checker output generated: " + os.getcwd() + "/" + file_name)
        murphifile.write(murphi_str)

    def gen_make(self):
        self.gen_makefile()

    def compile(self):
        self.set_make_muprhi_path()
        self.run_compilation()

    def compile_and_run(self, memory: int = 4000):
        self.gen_make()
        self.compile()
        self.run_murphi(memory)

    def run(self, memory: int = 4000) -> bool:
        return self.run_murphi(memory, False)

    def gen_makefile(self):
        makefile = open("Makefile", "w")
        murphi_file_name = self.file_name.split(".")[0]
        Debug.psection(f"{Debug.spacer} Generate Makefile {murphi_file_name}{TemplateHandler.nl}")
        compaction = "-b"

        replace_keys = [murphi_file_name, compaction]
        template = self._stringReplKeys(self._openTemplate(MurphiTemplates.f_tmp_make), replace_keys)

        makefile.write(template)
        makefile.flush()

    def set_make_muprhi_path(self):
        makefile = open("Makefile", "r+")
        makefile_str = makefile.read()
        makefile_str = self._stringRepl(makefile_str, 2, self.murphi_path)
        makefile.write(makefile_str)
        makefile.flush()

    def run_compilation(self):
        Debug.psection(f"Compile {self.file_name.split('.')[0]}{TemplateHandler.nl}")
        compile = subprocess.run(["make"], stdout=subprocess.PIPE).stdout.decode("utf-8")
        compilefile = open(self.file_name.split(".")[0] + "_compile" + ".txt", "w")
        compilefile.write(compile)
        compilefile.close()

        res = re.search(r'Makefile:[\w\s:]*\'[\w\s.]*\'\s*failed', compile)
        if res:
            self.pdebug(compile)
            self.perror("ProtoGen terminated due to Murphi compilation error")

    def run_murphi(self, memory: int, exec_error: bool = True):
        murphi_file_name = self.file_name.split(".")[0]
        Debug.psection(f"Start Murphi Modelchecker for {murphi_file_name}{TemplateHandler.nl}")
        if os.path.isfile("./" + murphi_file_name):
            cmd = ["./" + murphi_file_name, "-tv", "-pr", "-m", str(memory)]
            report = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode("utf-8")
            reportfile = open(murphi_file_name + "_results" + ".txt", "w")
            reportfile.write(report)
            reportfile.close()

            if not report:
                Debug.perror(f'Could not run Murphi for {os.getcwd()}/{murphi_file_name}.m')

            if "No error found" not in report:
                if exec_error:
                    print(report)
                    Debug.perror("Verification Failed, please see error trace")
                return False

        else:
            self.perror("Unable to locate murphi file in path: " + os.getcwd() + "/" + murphi_file_name)

        Debug.psuccess(self.name + " verification passed")
        return True

    def run_hash_murphi(self):
        pass

        '''        
        # Continous Murphi Run output stream
        if os.path.isfile("./" + murphiname):
            cmd = ["./" + murphiname, "-tv", "-pr", "-m", str(mem)]
            reportfile = open(murphiname + "_results" + ".txt", "w")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # Poll process for new output until finished
            while True:
                nextline = process.stdout.readline().decode("utf-8")
                reportfile.write(nextline)
                if nextline == '' and process.poll() is not None:
                    break
                print(nextline)

            output = process.communicate()[0]

            #report = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode("utf-8")
            reportfile.close()
            reportfile = open(murphiname + "_results" + ".txt", "r")
            report = reportfile.read()

            if "No error found" not in report:
                pdebug(report)
        '''
