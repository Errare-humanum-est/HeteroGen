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


class ProtoParserBase:
    terminal = 'terminal'
    k_undefined = 'undefined'

    # Datatypes
    k_init_val = 'INITVAL_'

    # DataTypes
    t_range = 'RANGE_'
    t_data = 'DATA_'
    t_id = 'ID_'
    t_msg = 'MSG_'
    t_set = 'OBJSET_'
    t_bool = 'BOOL_'
    t_int = 'INT_'
    t_adr = 'ADR_'
    t_set_val = 'SET_'

    # Keywords
    k_assign = 'ASSIGN_'
    k_data = t_data
    k_trans = 'TRANS_'
    k_guard = 'GUARD_'
    k_setfunc = 'SETFUNC_'
    k_access = 'ACCESS_'

    k_event = 'EVENT_'
    k_event_ack = 'EVENT_ACK_'

    k_stall = 'STALL_'
    k_undef = 'UNDEF_'

    k_break = 'BREAK_'               # Final state assignment
    k_endproc = 'ENDPROC_'
    k_endwhen = 'ENDWHEN_'

    k_cond = 'COND_'
    k_ncond = 'NCOND_'
    k_cond_end = 'ENDIF_'

    k_msg = 'MSGCSTR_'

    k_send = 'SEND_'
    k_mcast = 'MCAST_'
    k_bcast = 'BCAST_'
    kmbcast = [k_mcast, k_bcast]

    k_state = 'State'
    k_id = 'ID'

    k_stable = 'STABLE_'

    # PARSER TOKENS ####################################################################################################
    ProcessTree = {
        'AWAIT_': '_program_flow_fork',
        'IFELSE_': '_program_flow_fork',
        k_break: '_program_flow_end',
        k_endwhen: '_program_flow_end',
        k_endproc: '_program_flow_end',
    }

    ProcessTreeEnd = ['ENDIF_', 'ENDWHEN_', 'ENDPROC_']

    CondKeys = {
        k_cond: '_HandleCond',
        k_ncond: '_HandleCond',
    }

    # General Object functions
    f_objects = {
        t_set: '_obj_set_func',
        'INITSTATE_': '_init_state',
        t_data: '_data_func',
        t_int: '_int_func',
        t_bool: '_bool_func',
        t_id: '_id_func',
        t_msg: '_msg_func',
    }

    def __init__(self):
        pass
