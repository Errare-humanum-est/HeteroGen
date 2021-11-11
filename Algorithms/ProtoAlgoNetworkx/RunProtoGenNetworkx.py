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

import time
import os

import pickle

from Parser.NetworkxParser.ClassProtoParser import ProtoParser
from DataObjects.ClassLevel import Level
from Algorithms.ProtoAlgoNetworkx.ProtoNetworkxBase import ProtoNetworkxBase

from Debug.Monitor.MakeDir import make_dir
from Debug.Monitor.ClassDebug import Debug


def RunProtoGenNetworkx(file, filename) -> Level:

    graphdbgparser = True

    path = os.getcwd()
    make_dir("ProtoGen_Output")

    dbg = Debug(True)

    develop = 0
    if not develop:
        # Frontend
        dbg.p_header("PROTOGEN PARSER")
        parser = ProtoParser(file, filename, graphdbgparser, True)

        level = Level(parser, "L1")

        dbg.p_header(dbg.spacer + "PROTOGEN ALGORITHM v3")

        # Saving the objects:
        with open('objs.pkl', 'wb') as f:  # Python 3: open(..., 'wb')
            pickle.dump(level, f)
    else:
        # Getting back the objects:
        with open('objs.pkl', 'rb') as f:  # Python 3: open(..., 'rb')
            level = pickle.load(f)

    talgo = time.time()

    ProtoNetworkxBase(level, None, False, True)

    dbg.pdebug("ProtoGen runtime: " + str(time.time() - talgo) + '\n')
    dbg.p_header(dbg.spacer + "PROTOGEN BACKEND")

    os.chdir(path)

    return level
