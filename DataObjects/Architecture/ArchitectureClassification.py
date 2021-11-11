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
#
#


class ArchitectureClassification:

    k_cache = "Cache"
    k_dir = "Dir"
    k_mem = "Memory"

    def __init__(self, parser, arch_name: str):
        self.arch_type = self._test_arch(parser, arch_name)
        pass

    def _test_arch(self, parser, arch_name: str):
        if arch_name == parser.getCacheIdentifier():
            return self.k_cache
        elif arch_name == parser.getDirIdentifier():
            return self.k_dir
        elif arch_name == parser.getMemIdentifier():
            return self.k_mem
        elif arch_name == self.k_cache or arch_name == self.k_dir or arch_name == self.k_mem:
            return arch_name
        else:
            assert 0, "Unknown architecture classification"

    def test_cache(self) -> bool:
        if self.arch_type == self.k_cache:
            return True
        return False

    def test_dir(self) -> bool:
        if self.arch_type == self.k_dir:
            return True
        return False

    def test_mem(self) -> bool:
        if self.arch_type == self.k_mem:
            return True
        return False
