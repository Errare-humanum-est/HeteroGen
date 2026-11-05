#  Copyright (c) 2022.  Nicolai Oswald
#  Copyright (c) 2022.  University of Edinburgh
#  Copyright (c) 2026.  Systems Research Group @ TUM
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

#  Options of the SLICC back end that depend on the system the controllers are generated for (its
#  topology), not on the protocols. Set once per run by RunSLICCModular.

from dataclasses import dataclass

LLC_CLUSTER = "cluster"
LLC_BANKED = "banked"
LLC_RANGE = "range"

GEM5_V23 = "v23"
GEM5_V20 = "v20"


@dataclass
class BackendOptions:
    # How an L1 finds its LLC:
    #   cluster  one LLC per cluster, chosen by the L1's `<LLC>_id` parameter (SMP, NUMA);
    #   banked   the cluster's LLC is split into 2^l2_select_num_bits slices interleaved by address
    #            (Synapse multi-host scenario): mapAddressToRange(addr, <LLC>, l2_select_low_bit,
    #            l2_select_num_bits, <LLC>_id), with the slices of cluster c numbered c * 2^bits + i.
    #   range    as banked, but each slice owns a contiguous range of the physical address space:
    #            the selection bits are the top ones (Synapse S4 heterogeneous chiplets; alloy-gem5's
    #            RubySystem::getRealPhysMemBits() and getL2Bits(), so gem5 v20 only).
    llc_mapping: str = LLC_CLUSTER
    # gem5 the controllers are written for:
    #   v23  gem5 v23 (Synapse S1-S3 artifact, `gem5-S1_2_3`);
    #   v20  alloy-gem5, gem5 v20 (Synapse S4 artifact, `gem5-S4/alloy-gem5`): memory through
    #        queueMemoryRead/Write, the L1 driven by a DOSequencer whose release-consistency request
    #        types (LD_NT, LD_ACQ, ST_NT, ST_REL, atomics) are served as loads and stores, the message
    #        types alloy's MessageBuffer needs, SLICC v20 syntax. The templates that differ live in
    #        TempSLICC/<dir>_v20 and replace those of TempSLICC/<dir> (TemplateHandler).
    gem5: str = GEM5_V23
    # What an intermediate controller does with a request of a child that its block cannot serve
    # yet (the message type has no handler in the block's state, typically a transient one):
    #   False  recycle it: the message goes back to the queue and is examined again every
    #          recycleLatency cycles, each time as one of the controller's transitions;
    #   True   park it (stall_and_wait) and wake it up when the block enters a state with a handler
    #          for the requests (Util.parked_ports). The requests of a contended block then cost one
    #          transition per state change instead of one every recycleLatency cycles, and are
    #          served in arrival order.
    park_requests: bool = False


OPTIONS = BackendOptions()
