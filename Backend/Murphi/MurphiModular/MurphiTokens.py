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


class MurphiTokens:

    ''' Data types '''
    t_int = "int"
    t_bool = "boolean"

    k_message = "Message"

    k_machines = "Machines"

    ## GenAdrDef
    k_address = "Address"
    k_cl_val = "ClValue"
    k_scalar_set = "scalarset"

    ''' Variables '''
    v_adr = "adr"
    v_mach = "m"             # if you change this please change the template files too
    v_cbe = "cbe"
    v_evt = "evt"
    v_m_type = "mtype"
    v_in_msg = "inmsg"
    v_base_msg = "basemsg"
    v_src = "src"
    v_dst = "dst"

    # Suffixes
    k_state_label = "s_"                # state label: GenArchEnums
    k_event_label = "e_"                # event label: GenArchEnums
    k_vector = "v_"
    k_vector_cnt = "cnt_"
    k_instance = "i_"
    k_assign = ":="
    k_undefine = 'undefine'

    k_state = "State"

    ## GenConst
    c_val_cnt_const = "VAL_COUNT"
    c_adr_cnt_const = "ADR_COUNT"
    c_ordered_const = "O_NET_MAX"
    c_unordered_const = "U_NET_MAX"
    # Litmus
    c_cpu_cnt = "CPU_COUNT"
    c_instr_cnt = "INSTR_COUNT"

    ## GenAccess
    k_perm_type = "PermissionType"

    ## GenMessageTypes, GenMessage
    k_message_type = "MessageType"

    ## GenMachineSets
    k_obj_set = "OBJSET_"

    ## GenMessage
    m_adr = (v_adr, k_address)
    m_type = (v_m_type, k_message_type)
    m_src = (v_src, k_machines)
    m_dst = (v_dst, k_machines)
    base_msg = [m_adr, m_type, m_src, m_dst]

    ## GenNetwork
    k_net = "NET_"
    k_ordered = "Ordered"
    k_ordered_cnt = "Ordered_cnt"
    k_unordered = "Unordered"
    k_send_single = "Send_"
    k_send_multi = "Multicast_"
    k_send_broad = "Broadcast_"

    k_fifo = "FIFO"
    k_buffer = "buf_"

    ## GenMachines
    k_entry = "ENTRY_"
    k_event = "EVENT_"
    k_mach = "MACH_"
    k_object = "OBJ_"
    v_cache_block = "cb"

    ## GenEvent
    k_issue_event = "IssueEvent_"
    k_reset_event = "ResetEvent_"

    k_check_init_event = "TestEvent_"
    k_serve_init_event = "ServeEvent_"

    k_check_remote_event = ""
    k_serve_remote_event = ""

    ## Vector functions
    k_set_func = {
        "add": "AddElement_",
        "del": "RemoveElement_",
        "clear": "ClearVector_",
        "contains": "IsElement_",
        "empty": "HasElement_",
        "count": "VectorCount_"
    }

    ## GenPCCToMurphi
    k_if = "if"
    k_then = "then"
    k_else = "else"
    k_endif = "endif"

    ## General functionality
    k_function = "function"
    k_var = "var"
    k_begin = "begin"
    k_end = "end"
    k_return = "return"

    # GenMessageStateMachines
    k_case = "case"
    k_switch = "switch"
    k_end_switch = "endswitch"
    k_msg_func = "FSM_MSG_"
    k_access_func = "FSM_Access_"

    # Litmus Test
    k_cpu = "CPU"
    k_instr = "INSTR"
    k_check_access = "Check_access"

    # System Reset function
    k_system_reset = "System_Reset"
    k_reset_machines = "ResetMachine_"

    # Network ready function check
    f_network_ready = 'network_ready()'

