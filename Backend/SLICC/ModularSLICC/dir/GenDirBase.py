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

from Backend.SLICC.ModularSLICC.dir.GenDirHeader import GenDirHeader
from Backend.SLICC.ModularSLICC.dir.GenDirStateDecl import GenDirStateDecl
from Backend.SLICC.ModularSLICC.dir.GenDirEvents import GenDirEvents
from Backend.SLICC.ModularSLICC.dir.GenDirStruct import GenDirStruct
from Backend.SLICC.ModularSLICC.dir.GenDirTBE import GenDirTBE
from Backend.SLICC.ModularSLICC.dir.GenDirStaticFns import GenDirStaticFns
from Backend.SLICC.ModularSLICC.dir.GenDirOutPorts import GenDirOutPorts
from Backend.SLICC.ModularSLICC.dir.GenDirInPorts import GenDirInPorts
from Backend.SLICC.ModularSLICC.dir.GenDirFooter import GenDirFooter
from Backend.SLICC.ModularSLICC.dir.GenDirActions import GenDirActions
from Backend.SLICC.ModularSLICC.dir.GenDirTransitions import GenDirTransitions
from Debug.Monitor.ClassDebug import Debug


class GenDirBase(
        Debug,
        GenDirActions,
        GenDirTransitions,
        GenDirHeader,
        GenDirStateDecl,
        GenDirEvents,
        GenDirStruct,
        GenDirTBE,
        GenDirStaticFns,
        GenDirOutPorts,
        GenDirInPorts,
        GenDirFooter):

    def __init__(self, template_dir):
        Debug.__init__(self, debug_enabled=True)
        GenDirActions.__init__(self, template_dir)
        GenDirTransitions.__init__(self, template_dir)
        GenDirHeader.__init__(self, template_dir)
        GenDirStateDecl.__init__(self, template_dir)
        GenDirEvents.__init__(self, template_dir)
        GenDirStruct.__init__(self, template_dir)
        GenDirTBE.__init__(self, template_dir)
        GenDirStaticFns.__init__(self, template_dir)
        GenDirOutPorts.__init__(self, template_dir)
        GenDirInPorts.__init__(self, template_dir)
        GenDirFooter.__init__(self, template_dir)
