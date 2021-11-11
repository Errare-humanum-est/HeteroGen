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

from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.ClassLevel import Level

from DataObjects.Architecture.ClassFiniteStateMachine import FiniteStateMachine
from Algorithms.ControllerGeneration.ProxyDirController.GenProxyDirStateMachine import ProxyDirStateMachine

from Debug.Monitor.ClassDebug import Debug
from Debug.Monitor.ProtoCCTable import ProtoCCTablePrinter


class ProxyDirArchitecture(FlatArchitecture, ProxyDirStateMachine):

    def __init__(self, arch_level: Level, gdbg: bool = False):
        self.cache = arch_level.cache
        self.directory = arch_level.directory
        ProxyDirStateMachine.__init__(self, arch_level)
        self.merge_machine_definitions()

        FlatArchitecture.__init__(self, self.directory, gdbg)
        FlatArchitecture.copy_flat_architecture(self, self.directory)

        self.update_base_fsm(self.directory.init_state, set(self.proxy_dir_stable_states), set(self.proxy_dir_trans))

        fsm_states = self.get_architecture_states()
        fsm_trans = self.get_architecture_transitions()

        # Register the new proxy directory controller as the directory of the level replacing the previous directory
        arch_level.directory = self

        Debug.psection(f"ProxyDir controller for {arch_level.parser.filename}")
        ProtoCCTablePrinter().ptransitiontable(list(self.get_architecture_transitions()))

        #self.dbg_tree_graph(self.gen_graph(list(fsm_trans)))

        # The architecture is
    def get_arch_list(self):
        return [self, self.cache, self.directory]

    def merge_machine_definitions(self):
        # Update the machine definition of the proxy machine
        Debug.perror("Unable to generate proxy cache. Variables in cache and directory have identical identifiers",
                     set(self.directory.machine.variables.keys()).intersection(
                         self.cache.machine.variables))
        self.directory.machine.variables.update(self.cache.machine.variables)
        self.directory.machine.variables_init_val.update(
            self.cache.machine.variables_init_val)
        # Update the machine event definitions from the proxy cache
        Debug.perror("Unable to generate proxy cache. Events in cache and directory have identical identifiers",
                     set(self.directory.machine.variables.keys()).intersection(
                         self.cache.machine.variables))
        self.directory.event_network.event_issue.update(
            self.cache.event_network.event_issue)
        self.directory.event_network.event_ack.update(
            self.cache.event_network.event_ack)

    ####################################################################################################################
    # Hierarchical Functions
    ####################################################################################################################
    def get_flat_base_architecture(self):
        return self.directory

