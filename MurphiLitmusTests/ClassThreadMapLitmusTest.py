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
#
from typing import Tuple, Set, List, Union, Dict
from MurphiLitmusTests.ClassLitmusTest import LitmusTest, LitmusThread
from DataObjects.ClassMultiDict import MultiDict
from DataObjects.ClassMachine import Machine


class MachThreadMapLitmusTest(LitmusTest):

    def __init__(self, litmus_test_name: str, exists: bool):
        LitmusTest.__init__(self, litmus_test_name)
        self.permutation_str_list = []
        self.exists = exists
        self.cache_mach_to_thread_map: MultiDict = MultiDict()
        self.sorted_mach: Union[Tuple[Machine], None] = None

    def add_cache_mach_thread_map(self, cache_mach: Machine, litmus_thread: LitmusThread):
        self.cache_mach_to_thread_map[cache_mach] = litmus_thread
        self.add_thread(litmus_thread)
        self.remap_processor_thread()

    def remap_processor_thread(self):
        self.sorted_mach = tuple(sorted(self.cache_mach_to_thread_map.keys(), key=lambda x: str(x)))

        processor_ind = 0
        for arch in self.sorted_mach:
            # The processor IDs are now listed incrementally
            for thread in self.cache_mach_to_thread_map[arch]:
                self.threads[processor_ind] = thread
                processor_ind += 1




