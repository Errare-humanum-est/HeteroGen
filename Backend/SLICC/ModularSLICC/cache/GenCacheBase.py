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

from Backend.SLICC.ModularSLICC.cache.GenCacheHeader import GenCacheHeader
from Backend.SLICC.ModularSLICC.cache.GenCacheStateDecl import GenCacheStateDecl
from Backend.SLICC.ModularSLICC.cache.GenCacheEvents import GenCacheEvents
from Backend.SLICC.ModularSLICC.cache.GenCacheStruct import GenCacheStruct
from Backend.SLICC.ModularSLICC.cache.GenCacheTBE import GenCacheTBE
from Backend.SLICC.ModularSLICC.cache.GenCacheStaticFns import GenCacheStaticFns
from Backend.SLICC.ModularSLICC.cache.GenCacheOutPorts import GenCacheOutPorts
from Backend.SLICC.ModularSLICC.cache.GenCacheInPorts import GenCacheInPorts
from Backend.SLICC.ModularSLICC.cache.GenCacheFooter import GenCacheFooter
from Backend.SLICC.ModularSLICC.cache.GenCacheActions import GenCacheActions
from Backend.SLICC.ModularSLICC.cache.GenCacheTransitions import GenCacheTransitions
from Debug.Monitor.ClassDebug import Debug


class GenCacheBase(
        Debug,
        GenCacheHeader,
        GenCacheStateDecl,
        GenCacheEvents,
        GenCacheStruct,
        GenCacheTBE,
        GenCacheStaticFns,
        GenCacheOutPorts,
        GenCacheInPorts,
        GenCacheFooter,
        GenCacheActions,
        GenCacheTransitions):

    def __init__(self, template_dir):
        Debug.__init__(self, debug_enabled=True)
        GenCacheHeader.__init__(self, template_dir)
        GenCacheStateDecl.__init__(self, template_dir)
        GenCacheEvents.__init__(self, template_dir)
        GenCacheStruct.__init__(self, template_dir)
        GenCacheTBE.__init__(self, template_dir)
        GenCacheStaticFns.__init__(self, template_dir)
        GenCacheOutPorts.__init__(self, template_dir)
        GenCacheInPorts.__init__(self, template_dir)
        GenCacheFooter.__init__(self, template_dir)
        GenCacheActions.__init__(self, template_dir)
        GenCacheTransitions.__init__(self, template_dir)
