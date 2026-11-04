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
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler


class GenMachineEvents:

    @staticmethod
    def gen_progress_event(temp_h: TemplateHandler) -> str: return f"Progress, desc=\"Progress, please!\"{temp_h.end}"

    @staticmethod
    def gen_stall_event(temp_h: TemplateHandler, port: str) -> str:
        return f"Stall{port}, desc=\"Stall the {port} port.\"{temp_h.end}"

    @staticmethod
    def gen_cache_alloc_event(temp_h: TemplateHandler) -> str:
        return f"allocCacheEntry, desc=\"Allocate a new cache entry.\"{temp_h.end}"

    @staticmethod
    def gen_tbe_alloc_event(temp_h: TemplateHandler) -> str:
        return f"allocTBE, desc=\"Allocate a new TBE.\"{temp_h.end}"

    @staticmethod
    def gen_tbe_dealloc_event(temp_h: TemplateHandler) -> str:
        return f"deallocTBE, desc=\"Deallocate a TBE.\"{temp_h.end}"

    @staticmethod
    def silent_evict_event(temp_h: TemplateHandler) -> str:
        return f"deallocevict, desc=\"Deallocate cache block before completion ack for eviction request.\"{temp_h.end}"
