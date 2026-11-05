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

from typing import Set, Dict, Tuple, List
from collections import OrderedDict
from DataObjects.ClassCluster import Cluster
from DataObjects.States.ClassStatev2 import State_v2
from DataObjects.Transitions.ClassTransitionv2 import Transition_v2
from Backend.SLICC.ModularSLICC import SLICCTokens
from Backend.SLICC.ModularSLICC.TemplateClass import TemplateHandler
from Algorithms.HeteroGen.ArchTupleStateOrdering import ArchTupleStateOrdering
from Algorithms.HeteroGen.ClassHHDirArchitecture import HHDirArchitecture
from Backend.SLICC.ModularSLICC.BackendOptions import OPTIONS
from DataObjects.Architecture.ClassFlatArchitecture import FlatArchitecture
from DataObjects.Architecture.ClassGlobalBaseArchitecture import GlobalBaseArchitecture
from DataObjects.FlowDataTypes.ClassBaseAccess import Access
from DataObjects.States.ClassCompoundState import CompoundState
from Parser.DataTypes.ClassBaseNetwork import BaseMessage
from Parser.DataTypes.ClassProtoMachine import ProtoMachine
from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase
from Parser.ProtoCCcomTreeFct import toStringList

def proxy_entry_alloc(arch: FlatArchitecture, transition: Transition_v2) -> Tuple[bool, bool]:
    """(allocate, refresh_mru) for a transition of a synthesized controller: whether it allocates the
    cache entry, and whether it refreshes the entry's replacement state (Synthesis.entry_alloc)."""
    return arch.entry_alloc(transition)


def get_compound_perms(arch: FlatArchitecture, state: CompoundState, default: str | None = None) -> list[tuple[FlatArchitecture, set[str]]]:
    assert isinstance(arch, ArchTupleStateOrdering)
    accesses = []
    for sub_state in state.base_states:
        sub_arch = arch.get_arch_by_state(sub_state)
        accesses.append((sub_arch, get_arch_access_perms(sub_arch, sub_state, default)))
    return accesses

def get_arch_access_perms(arch: FlatArchitecture, state: State_v2, default: str | None = None) -> set[str]:
    if isinstance(state, CompoundState):
        return set.union(*[p for _, p in get_compound_perms(arch, state, default)])
    else:
        t = arch.stable_state_access_permission_map.get(state, {default} if default else {})
        return set(str(a) for a in t)

def get_invalid_states(arch: FlatArchitecture) -> Set[State_v2]:
    if isinstance(arch, HHDirArchitecture):
        for i, c in enumerate(arch.arch_tuple):
            if c.machine.mach_type == ProtoMachine.k_cache:
                cs = get_invalid_states(c)
                r = set([state for state in arch.get_architecture_stable_states() if state.base_states[i] in cs])
                return r
        assert False, "HH Dirs should have a cache"
    stable_state_perms = [(state, get_arch_access_perms(arch, state))
                          for state in arch.get_architecture_stable_states()]
    # A stable state without permissions other than the initial one keeps a copy the protocol does
    # not track (MESI-RC V): its entry stays allocated
    invalid_states = {state
                      for state, perms in stable_state_perms
                      if "load" not in perms and "store" not in perms
                      and (arch.init_state is None or str(state) == str(arch.init_state))}
    return invalid_states


def get_evict_trans_states(arch: FlatArchitecture) -> Set[State_v2]:
    evict_states = set()
    for state in arch.get_architecture_states_verified():
        if not state.stable and state.start_state_set:
            stable_state = state.start_state_set[0].stable_state
            accesses_stable_state = get_arch_access_perms(arch, stable_state)
            if len(accesses_stable_state) > 0 and state.end_state_set:
                if state.end_state_set[0].stable_state.state == "I":
                    evict_states.add(state)

    return evict_states

def get_evict_trans_states_all(arch: FlatArchitecture) -> Set[State_v2]:
    evict_states = set()
    for state in arch.get_architecture_states_verified():
        if not state.stable and state.start_state_set:
            if state.end_state_set:
                if state.end_state_set[0].stable_state.state == "I":
                    evict_states.add(state)

    return evict_states

def proxy_evict_states(arch: FlatArchitecture) -> Set[str]:
    """Compound states of a generated proxy in which its cache part is evicting the block (the
    eviction request has been sent and only its acknowledgement is awaited). The entry is freed when
    they are entered (`deallocevict`): the data, if still needed, stays in the TBE."""
    if not isinstance(arch, HHDirArchitecture):
        return set()
    caches = [a for a in arch.arch_tuple if a.machine.mach_type == ProtoMachine.k_cache]
    if not caches:
        return set()
    evicting = {str(state) for state in get_evict_trans_states_all(caches[0])}
    states = set()
    for state in arch.get_architecture_states_verified():
        if isinstance(state, CompoundState) and any(str(base) in evicting for base in state.base_states):
            states.add(str(state))
    return states


def get_states_following_invalid_states(arch: FlatArchitecture) -> Set[State_v2]:
    invalid_states = get_invalid_states(arch)
    next_states = set()
    for state in invalid_states:
        for trans in state.getaccess():
            next_state = trans.final_state
            if next_state.stable:
                continue  # a direct access (get_direct_access_events): nothing to allocate
            next_states.add(next_state)
    return next_states


def _get_hit_events(arch: FlatArchitecture) -> Dict[str, List[Tuple[str, str]]]:
    res = {"load": [], "store": [], "ifetch":[]}
    res.update({access: [] for access in rc_accesses(arch)})
    for state in arch.get_architecture_stable_states():
        for access in state.getaccesshit():
            assert access.final_state in arch.get_architecture_stable_states()
            access_type = str(access.guard)
            if access_type in res:
                start_s = str(access.start_state)
                end_s = str(access.final_state)
                res[access_type].append((start_s, end_s))

    return res


def get_local_hit_events(arch: FlatArchitecture) -> Dict[Tuple[str, str], Tuple[str, str]]:
    def _gen_event_name(start_s: str, end_s: str, access_name: str) -> str:
        return f"{start_s}{access_name}{end_s}Event"

    res = {}
    for access, transitions in sorted(_get_hit_events(arch).items()):
        for start_state, end_state in transitions:
            res[(access, start_state)] = (end_state, _gen_event_name(start_state, end_state, access))

    return res


def get_remote_hit_events_port(arch: FlatArchitecture, in_port: str) -> Dict[Tuple[str, str], str]:
    def _gen_event_name(end_s: str, access_name: str, port_name: str) -> str:
        return f"external{access_name}{end_s}{port_name}"

    res = {}
    for access, transitions in sorted(_get_hit_events(arch).items()):
        for _, end_state in transitions:
            res[(access, end_state)] = _gen_event_name(end_state, access, in_port)
    for access, end_state in sorted(rc_remote_completions(arch)):
        res[(access, end_state)] = _gen_event_name(end_state, access, in_port)
    return res


# Accesses of release-consistency code (Synapse S4, MESI-RC) and the alloy-gem5 DOSequencer request
# types they serve (gem5 v20): non-temporal loads, acquire loads, non-temporal and release stores.
# A protocol that does not declare them gets these requests as loads and stores. Each completes as
# a load (read callback) or a store (write callback, after writing its bytes into the block itself:
# alloy-gem5's sequencer does not write them, RubyRequest.WTData, writeMask).
RC_ACCESSES = {"ntload": ("load", ("LD_NT",)), "acqload": ("load", ("LD_ACQ",)),
               "ntstore": ("store", ("ST_NT", "ST_REL"))}


def transition_access(transition: Transition_v2) -> str:
    """The access of an access transition (some transitions of a new access, rebuilt by the
    synthesis, keep it only as their guard)."""
    return str(transition.access) if transition.access is not None else str(transition.guard)


def arch_accesses(arch: FlatArchitecture) -> Set[str]:
    return {transition_access(transition) for state in arch.get_architecture_states_verified()
            for transition in state.getaccess()}


def rc_accesses(arch: FlatArchitecture) -> List[str]:
    accesses = arch_accesses(arch) if not isinstance(arch, HHDirArchitecture) \
        else set()
    return sorted(access for access in RC_ACCESSES if access in accesses)


def access_kind(access: str) -> str:
    """load, store or ifetch: the callback that completes the access."""
    return RC_ACCESSES[access][0] if access in RC_ACCESSES else access


def is_rc_store(access: str) -> bool:
    return access in RC_ACCESSES and access_kind(access) == "store"


def access_statements(transition: Transition_v2) -> Set[str]:
    """The read/write statements (`load;`, `store;`, `ifetch;`) a transition executes."""
    found = set()
    for op in transition.operations[1:]:
        if str(op) == ProtoParserBase.k_access:
            found.add(str(op.getChildren()[0]))
        elif str(op) in ("load", "store", "ifetch"):
            found.add(str(op))
    return found


def rc_remote_completions(arch: FlatArchitecture) -> Set[Tuple[str, str]]:
    """(access, stable state) in which a response completes an access of release-consistency code
    that the state does not grant (MESI-RC: DataNT completes ntload in the untracked copy V)."""
    completions = set()
    accesses = rc_accesses(arch)
    if not accesses:
        return completions
    for transition in arch.get_architecture_transitions():
        if transition.start_state.stable or not transition.final_state.stable \
                or isinstance(transition.guard, Access):
            continue
        tokens = str(transition.start_state).split("_")
        for access in accesses:
            if access in tokens and access_kind(access) in access_statements(transition):
                completions.add((access, str(transition.final_state)))
    return completions


def get_direct_access_events(arch: FlatArchitecture) -> Dict[Tuple[str, str], Tuple[str, str]]:
    """Accesses served by sending a message without waiting for a reply (MESI-RC: ntstore from I, V,
    S writes the bytes through to the directory; ntload from I, V asks for the block, whose value
    the sequencer discards): (access, start state) -> (final state, event). They complete at once,
    from the mandatory queue, with the callback of the read/write statement they execute."""
    res = {}
    for state in arch.get_architecture_stable_states():
        for transition in state.getaccessmiss():
            if transition.final_state.stable:
                access, start, end = transition_access(transition), str(state), str(transition.final_state)
                assert access in RC_ACCESSES or access_kind(access) in access_statements(transition), \
                    f"{access} from {start} completes without its {access_kind(access)} statement"
                res[(access, start)] = (end, f"{start}{access}{end}Direct")
    return res


def direct_action_name(access: str, start: str, end: str) -> str:
    """The action with the operations of a direct access (several accesses may go V -> V)."""
    return f"action{start}_{access}_{end}"


def uncached_direct_accesses(arch: FlatArchitecture) -> Set[Tuple[str, str]]:
    """Direct accesses from a state without the block that leave it without the block (MESI-RC
    ntstore from I): served from a TBE, with no cache entry and no victim."""
    invalid_states = {str(state) for state in get_invalid_states(arch)}
    return {(access, start) for (access, start), (end, _) in get_direct_access_events(arch).items()
            if start in invalid_states and end in invalid_states}


def hit_action(access: str) -> str:
    """Suffix of the local hit action of an access (local_<suffix>Hit): a store of release-
    consistency code writes its bytes itself (local_ntstoreHit)."""
    return access if is_rc_store(access) else access_kind(access)


def silent_victim_states(arch: FlatArchitecture) -> Set[str]:
    """States holding a copy that is evicted without a message (MESI-RC V): the victim entry is
    freed at once, from the mandatory queue (deallocmandatory_in)."""
    invalid_states = get_invalid_states(arch)
    return {str(state) for state in arch.get_architecture_stable_states()
            for transition in state.getevict()
            if state not in invalid_states and transition.final_state in invalid_states
            and not transition.out_msg}


_PARTIAL: Dict[int, Set[str]] = {}


def partial_messages(arch: GlobalBaseArchitecture) -> Set[str]:
    """Messages that carry only the bytes written by a store of release-consistency code, with its
    write mask: the stores' own requests (MESI-RC PutNT) and the forwarded requests that pass the
    bytes on to a cache, which merges them into its copy (Fwd_PutNT). Their data is merged
    (mergeCacheBlock), and they take the write mask of the request that causes them."""
    if id(arch) not in _PARTIAL:
        partial: Set[str] = set()
        archs = arch.get_dependent_architectures()
        for other in archs:
            for transition in other.get_architecture_transitions():
                if isinstance(transition.guard, Access) and is_rc_store(str(transition.guard)):
                    partial.update(str(msg) for msg in transition.out_msg if msg.has_data())
        if partial:
            data_var = get_message_data_var(arch)
            for other in archs:
                if isinstance(other, HHDirArchitecture) \
                        or not other.machine.check_cache():
                    continue
                for transition in other.get_architecture_transitions():
                    guard = str(transition.guard)
                    # an owner merging the bytes into its copy (not the data of a read, e.g. MESI-RC
                    # DataNT filling the untracked copy V)
                    if not transition.start_state.stable or isinstance(transition.guard, Access) \
                            or "store" not in get_arch_access_perms(other, transition.start_state):
                        continue
                    line = get_active_cache_line(other)
                    for op in transition.operations[1:]:
                        tokens = toStringList(op)
                        if str(op) == ProtoParserBase.k_assign and str(op.getChildren()[0]) == line \
                                and any(tokens[i:i + 3] == [guard, ".", data_var] for i in range(len(tokens) - 2)):
                            partial.add(guard)
        _PARTIAL[id(arch)] = partial
    return _PARTIAL[id(arch)]


def get_active_cache_line(arch: FlatArchitecture) -> str:
    # The protocols do not say which Data variable an access that hits reads or writes: every cache
    # has exactly one field of type Data, and a hit uses it.
    active_line = None
    var_defs = arch.machine.variables.values()
    for var_def in var_defs:
        if var_def.getText() == SLICCTokens.t_DATA:
            assert active_line is None  # There must be a UNIQUE cache line for the line, see above comment
            active_line = var_def.getChildren()[-1].getText()
    assert active_line is not None
    return active_line


def get_message_data_var(arch: GlobalBaseArchitecture) -> str:
    # Similar to get_active_cache_line, we sometimes also need to know precisely which data object
    # in a message is being read from or written to.
    # We therefore assume that the different message types COLLECTIVELY define a single, unique
    # cache line / data block.
    data_var = None
    for msg_type in arch.network.msg_types.values():
        for var, var_type_tree in msg_type.msg_vars.items():
            if str(var_type_tree) == SLICCTokens.t_DATA:
                assert data_var is None or data_var == var, \
                    f"Messages define more than one data block; had {data_var}, found {var}."
                data_var = var

    assert data_var is not None, "Messages define no data block?"
    return data_var


_USED_NETWORKS: Dict[int, Set[str]] = {}


def _sent_messages(arch: FlatArchitecture):
    """(network, message type) of every message `arch` sends."""
    for transition in arch.get_architecture_transitions():
        operations = transition.operations
        for idx, op in enumerate(operations):
            if str(op) == 'MCAST_' or str(op) == 'SEND_':
                msg_name = str(op.getChildren()[1])
                for op2 in reversed(operations[:idx]):
                    if str(op2) == 'ASSIGN_' and str(op2.getChildren()[0]) == msg_name:
                        yield str(op.getChildren()[0]), str(op2.getChildren()[2].getChildren()[1])
                        break


def used_networks(arch: FlatArchitecture) -> Set[str]:
    """Networks on which `arch` sends a message or from which it receives one. A machine declares
    the buffers and ports of these only: e.g. the L1s below a CXL LLC never see the CXL channels.
    With a single protocol every machine uses every network."""
    if id(arch) not in _USED_NETWORKS:
        msg_networks: Dict[str, Set[str]] = {}
        for other in arch.global_arch.get_dependent_architectures():
            for network, msg_type in _sent_messages(other):
                msg_networks.setdefault(msg_type, set()).add(network)
        used = {network for network, _ in _sent_messages(arch)}
        for transition in arch.get_architecture_transitions():
            used |= msg_networks.get(str(transition.guard), set())
        _USED_NETWORKS[id(arch)] = used
    return _USED_NETWORKS[id(arch)]


def get_in_ports(arch: FlatArchitecture, cache: bool) -> 'OrderedDict[str, str]':
    def _gen_port_name(network_name: str) -> str:
        # Might want to consider something more sophisticated for this
        return network_name.lower() + "_in"

    in_ports = OrderedDict()
    if cache:
        direction = "From"
    else:
        direction = "To"


    # Two merged protocols may declare the same network as ordered in one and unordered in the
    # other (e.g. MESI_unord and MESIF_unord): it is one network, kept ordered.
    used = used_networks(arch)
    for net in list(arch.global_arch.network.ordered_networks.keys()) + \
            list(arch.global_arch.network.unordered_networks.keys()):
        if used and net not in used:
            continue
        net_name = net + direction
        if net_name not in in_ports:
            in_ports[net_name] = _gen_port_name(net_name)

    return in_ports


def get_out_ports(arch: FlatArchitecture, cache: bool) -> 'OrderedDict[str, str]':
    def _gen_port_name(network_name: str) -> str:
        # Might want to consider something more sophisticated for this
        return network_name.lower() + "_out"

    out_ports = OrderedDict()
    if cache:
        direction = "To"
    else:
        direction = "From"


    # Two merged protocols may declare the same network as ordered in one and unordered in the
    # other (e.g. MESI_unord and MESIF_unord): it is one network, kept ordered.
    used = used_networks(arch)
    for net in list(arch.global_arch.network.ordered_networks.keys()) + \
            list(arch.global_arch.network.unordered_networks.keys()):
        if used and net not in used:
            continue
        net_name = net + direction
        if net_name not in out_ports:
            out_ports[net_name] = _gen_port_name(net_name)

    return out_ports


def gen_stall_str(temp_h: TemplateHandler, cache: bool, port: str) -> str:
    if cache:
        return f"trigger(Event:Stall{port}, LineAddress, getEntry(LineAddress), tbe){temp_h.sem}"
    else:
        return f"trigger(Event:Stall{port}, LineAddress, tbe){temp_h.sem}"

def gen_silent_evict(temp_h: TemplateHandler) -> str:
    return f"trigger(Event:deallocevict, LineAddress, getEntry(LineAddress), tbe){temp_h.sem}"


def gen_recycle_str(temp_h: TemplateHandler, cache: bool, port: str) -> str:
    return f'DPRINTF(RubySlicc, "recycling %s on {port} (addr: %#x)\\\\n", st, LineAddress);{temp_h.nl}' \
           f"{port}.recycle(clockEdge(), cyclesToTicks(recycleLatency));{temp_h.nl}" \
           f"{gen_progress_str(temp_h, cache)}"

def gen_progress_str(temp_h: TemplateHandler, cache: bool) -> str:
    if cache:
        return f"trigger(Event:Progress, LineAddress, getEntry(LineAddress), tbe){temp_h.sem}"
    else:
        return f"trigger(Event:Progress, LineAddress, tbe){temp_h.sem}"


def gen_tbe_alloc_str(temp_h: TemplateHandler, cache: bool) -> str:
    if cache:
        return f"trigger(Event:allocTBE, LineAddress, getEntry(LineAddress), tbe){temp_h.sem}"
    else:
        return f"trigger(Event:allocTBE, LineAddress, tbe){temp_h.sem}"


def gen_tbe_dealloc_str(temp_h: TemplateHandler, cache: bool) -> str:
    if cache:
        return f"trigger(Event:deallocTBE, LineAddress, getEntry(LineAddress), tbe){temp_h.sem}"
    else:
        return f"trigger(Event:deallocTBE, LineAddress, tbe){temp_h.sem}"


def must_access_memory(cache: bool) -> bool:
    """
    Checks whether a given architecture must access main memory in order to read/write data.
    :param arch: The architecture to investigate.
    :param level: The level which the architecture lies in.
    :return: A boolean matching the truthfulness of the statement "this architecture must access main memory".
    """
    return not cache


def reverse_direction(direction: str) -> str:
    return "From" if direction == "To" else "To"


def _persistent_variable(arch: FlatArchitecture, var_name: str) -> bool:
    """A machine variable that outlives a transaction, i.e. an identifier or a set (the owner, the
    sharers, the MESIF forwarder), kept in the cache entry; integers (ack counters) are per
    transaction and live in the TBE."""
    tree = arch.machine.variables.get(var_name)
    return tree is not None and (str(tree) == "ID_" or "SET_" in str(tree.toStringTree()))


def get_entry_variable(arch: FlatArchitecture, cache: bool, var_name: str, var_str: str) -> str:
    # Variable is stored in the cache entry if we are a dir or if it is the cache line.
    # Otherwise, it should be kept in the TBE/MSHR.
    if not cache or var_name == get_active_cache_line(arch) or isinstance(arch, HHDirArchitecture):
        if arch.machine.mach_id == "cache":
            if var_str == "cl" :
                return "getCacheBlock(tbe, getEntry(LineAddress), LineAddress)"
            elif var_str == "cl_in_msg" :
                return "setCacheBlock(tbe, getEntry(LineAddress), LineAddress, in_msg.cl);"
            else:
                return "getCacheBlock(tbe, getEntry(LineAddress), LineAddress)"
        elif arch.machine.mach_id != "cache" and isinstance(arch, HHDirArchitecture):
            if var_str == "cl" :
                return "getCacheBlock(tbe, getEntry(LineAddress), LineAddress)"
            elif "owner" in var_name or "cache" in var_name or "proxy" in var_name \
                    or _persistent_variable(arch, var_name):
                return f"getEntry(LineAddress).{var_str}"
            elif "getCacheBlock(tbe, getEntry(LineAddress), LineAddress)" in var_str:
                return f"//getEntry(LineAddress).{var_str}"
            elif var_name == get_active_cache_line(arch) and "in_msg" in var_str:
                # Only the cache line itself is written through setCacheBlock; any other variable
                # assigned from the incoming message (e.g. acksExpected) lives in the TBE.
                return "setCacheBlock(tbe, getEntry(LineAddress), LineAddress, in_msg.cl);"
            else:
                return f"tbe.{var_str}"
        else:
            return f"getEntry(LineAddress).{var_str}"
    else:
        # accessing the tbe requires it to be valid, of course
        return f"tbe.{var_str}"


def check_tbe_valid(temp_h: TemplateHandler, cache: bool, port: str) -> str:
    return f"if (is_invalid(tbe)) {{{temp_h.nl}" \
           f"{temp_h.tab}if (TBEs.areNSlotsAvailable(1, clockEdge())) {{{temp_h.nl}" \
           f"{temp_h.tab * 2}{gen_tbe_alloc_str(temp_h, cache)}{temp_h.nl}" \
           f"{temp_h.tab}}} else {{{temp_h.nl}" \
           f"{temp_h.add_tabs(gen_recycle_str(temp_h, cache, port), 2)}{temp_h.nl}" \
           f"{temp_h.tab}}}{temp_h.nl}}}"


def check_cache_valid(temp_h: TemplateHandler) -> str:
    #return f"if (is_invalid(cache_entry)) {{{temp_h.nl}" \
    #       f"{temp_h.tab}if (cache.cacheAvail(in_msg.addr)) {{{temp_h.nl}" \
    #       f"{temp_h.tab * 2}{gen_tbe_alloc_str(temp_h, cache)}{temp_h.nl}" \
    #       f"{temp_h.tab}}} else {{{temp_h.nl}" \
    #       f"{temp_h.tab * 2}{gen_stall_str(temp_h, cache, port)}{temp_h.nl}" \
    #       f"{temp_h.tab}}}{temp_h.nl}}}"#
    return f"if (is_invalid(getEntry(LineAddress))) {{{temp_h.nl + temp_h.tab}trigger(Event:allocCacheEntry, LineAddress, getEntry(LineAddress), tbe);{temp_h.nl}}}"


def proxy_key_fields(arch, key: str = None) -> 'OrderedDict[str, str]':
    """Fields of a deferred message (proxy_msg<level>) that are kept in the cache entry: the sender
    and every payload field of the protocol's messages (e.g. the acksExpected or the data of a
    deferred MOESI response), and the write mask if the level of `key` has partial messages."""
    fields = OrderedDict(SLICCTokens.proxy_key_fields)
    kept = (ProtoParserBase.t_int, ProtoParserBase.t_bool, ProtoParserBase.t_id, ProtoParserBase.t_data)
    for msg_type in arch.global_arch.network.msg_types.values():
        for name, var_type in msg_type.msg_vars.items():
            if str(var_type) in kept and name not in fields:
                fields[name] = str(var_type)
    level = key[len("proxy_msg"):] if key else ""
    if any(msg.endswith(level) for msg in partial_messages(arch.global_arch)):
        fields[SLICCTokens.write_mask] = SLICCTokens.st_write_mask
    return fields


_READ_DATA: Dict[int, Set[str]] = {}


def messages_with_read_data(arch: GlobalBaseArchitecture) -> Set[str]:
    """Messages whose data block some machine of the system reads (an operation mentions
    `<message>.<data>`). Only these carry the block; for the others the data the protocol puts in
    the message is not sent (e.g. MESIF PutS/PutE carry the block for an exclusive controller
    above the caches; elsewhere nobody reads it, and they stay control messages)."""
    if id(arch) not in _READ_DATA:
        data_var = get_message_data_var(arch)
        messages = set(arch.network.base_message_dict.keys())
        read: Set[str] = set()
        for other in arch.get_dependent_architectures():
            for transition in other.get_architecture_transitions():
                for op in transition.operations:
                    tokens = toStringList(op)
                    for i in range(len(tokens) - 2):
                        if tokens[i] in messages and tokens[i + 1] == "." and tokens[i + 2] == data_var:
                            read.add(tokens[i])
        _READ_DATA[id(arch)] = read
    return _READ_DATA[id(arch)]


def drop_unread_data(message_dict: Dict[str, str], arch: GlobalBaseArchitecture):
    """Removes the data block from a message to be sent if no machine reads it (see above)."""
    data_var = get_message_data_var(arch)
    msg_name = message_dict.get("Type", "").split(":")[-1]
    if data_var in message_dict and msg_name not in messages_with_read_data(arch):
        message_dict.pop(data_var)


def get_message_size(message_dict: Dict[str, str], arch: GlobalBaseArchitecture) -> str:
    if get_message_data_var(arch) in message_dict.keys() \
            and message_dict.get("Type", "").split(":")[-1] not in partial_messages(arch):
        return "MessageSizeType:Data"
    else:
        return "MessageSizeType:Control"

def parked_ports(cluster: Cluster, arch: FlatArchitecture,
                 in_ports: 'OrderedDict[str, str]') -> 'OrderedDict[str, List[str]]':
    """Back-end option `park_requests`: the in ports of an intermediate controller whose stalled
    messages are parked (stall_and_wait) instead of recycled, each with the states that have a
    handler for a message of the port.

    The ports are those of the children's requests: the ones carrying the messages that can
    allocate the block here. A message is stalled when its type has no handler in the state of its
    block (GenMachineInPorts; a missing victim or TBE recycles in line instead), so a parked message
    can only be consumed once the block is in a state with a handler for its port: the controller
    wakes the messages parked for a block when the block enters one of these states."""
    parked = OrderedDict()
    if not OPTIONS.park_requests:
        return parked
    transitions = arch.get_architecture_transitions()
    alloc_msgs = {str(t.guard) for t in transitions if proxy_entry_alloc(arch, t)[0]}
    for network, msgs in sorted(get_msg_port_mapping(cluster).items()):
        port = in_ports.get(network + "From")
        if port is None or not alloc_msgs & msgs:
            continue
        parked[port] = sorted({str(t.start_state) for t in transitions
                               if isinstance(t.guard, BaseMessage) and str(t.guard) in msgs
                               and str(t.guard) in arch.global_arch.network.base_message_dict})
    return parked


def get_msg_port_mapping(cluster: Cluster) -> dict[str, set[str]]:
    msgs = {}
    for archss in cluster.get_machine_architectures():
        archs = archss.global_arch.get_dependent_architectures()
        for arch in archs:
            for transition in arch.get_architecture_transitions():
                operations = transition.operations
                for idx, op in enumerate(operations):
                    if str(op) == 'MCAST_' or str(op) == 'SEND_':
                        network = str(op.getChildren()[0])
                        msg_name = str(op.getChildren()[1])
                        msg_type = None
                        for op2 in reversed(operations[:idx]):
                            if str(op2) == 'ASSIGN_' and str(op2.getChildren()[0]) == msg_name:
                                msg_ctor = op2.getChildren()[2]
                                assert str(msg_ctor) == 'MSGCSTR_'
                                msg_type = str(msg_ctor.getChildren()[1])
                                break
                        assert msg_type is not None
                        msgs.setdefault(network, set()).add(msg_type)
    return msgs
