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

from Parser.NetworkxParser.ClassProtoParserBase import ProtoParserBase

# SLICC Types
st_mach_id = "MachineID"
st_net_dest = "NetDest"
st_int = "int"
st_data = "DataBlock"
st_write_mask = "WriteMask"
st_bool = "bool"

# SLICC constant variable names
k_in_msg = "in_msg"
k_out_msg = "out_msg"
# Quick hack to allow the keyword undefined in the Murphi input for now
k_mur_def = "undefined"
k_if = "if"
k_elsif = "else if"
k_else = "else"
k_entry = "entry"
k_mach = "machineID"

# ProtoGen Parser Node Types
t_INITSTATE = "INITSTATE_"
t_DATA = "DATA_"
t_MSGCSTR = "MSGCSTR_"
t_SETFUNC = "SETFUNC_"
t_MODSTATEFUNC = "MODSTATEFUNC_"
t_COND = "COND_"
t_NCOND = "NCOND_"
t_ELSE = "ELSE_"  # Not actually present in ProtoGen but shoe-horned in by [GenMachineInPorts.restructure_branches].
t_ASSIGN = "ASSIGN_"
t_SEND = "SEND_"
t_MCAST = "MCAST_"
t_BCAST = "BCAST_"

# PCC -> SLICC translations
data_type_map = {
    'OBJSET_': '_pass_node',
    t_INITSTATE: '_set_init_state',
    t_DATA: '_gen_cache_line',
    'ID_': '_gen_identifier',
    'INT_': '_gen_int',
    'BOOL_': '_gen_bool',
    'MSG_': '_gen_msg',
}
set_func_map = {
    'add': '_gen_vector_add',
    'del': '_gen_vector_delete',
    'clear': '_gen_vector_clear',
    'contains': '_gen_vector_contains',
    'empty': '_gen_vector_empty',
    'count': '_gen_vector_count',
    'smallest': '_gen_vector_smallest',
}
op_map = {
    ('==', False): '==',
    ('>=', False): '>=',
    ('<=', False): '<=',
    ('!=', False): '!=',
    ('<', False): '<',
    ('>', False): '>',
    ('==', True): '!=',
    ('>=', True): '<',
    ('<=', True): '>',
    ('!=', True): '==',
    ('<', True): '>=',
    ('>', True): '<=',
}

access_map = {
    'load': 'read',
    'store': 'write',
}
field_map = {
    'src': 'Sender',
    'dest': 'Destination',
}

base_message_vars = {
    "adr": ProtoParserBase.t_adr,
    "src": ProtoParserBase.t_id,
    "dst": ProtoParserBase.t_id,
}

proxy_key_fields = {
    "src": ProtoParserBase.t_id,
    # "exclusiveL1": ProtoParserBase.t_bool,
}

# Write mask of a partial message (Util.partial_messages): field of CoherenceMessage and of the
# deferred request of a proxy
write_mask = "writeMask"
