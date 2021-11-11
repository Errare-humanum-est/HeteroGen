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

from typing import List

from Backend.Common.GenPCCToBase import GenPCCToBase
from Backend.Murphi.MurphiModular.MurphiTokens import MurphiTokens
from Debug.Monitor.ClassDebug import Debug


class GenPCCToMurphi(GenPCCToBase):

    def __init__(self):
        GenPCCToBase.__init__(self)

    ''' General functions '''
    ## New line placeholder
    @staticmethod
    def gen_nl() -> str:
        return GenPCCToBase.nl

    ## End statement placeholder
    @staticmethod
    def gen_end() -> str:
        return GenPCCToBase.end

    ''' Variable declarations '''
    ## Variable declaration function place holder
    @staticmethod
    def gen_var_decl_func(var: str = '', var_type: str = '', val: str = '') -> str:
        return f"{MurphiTokens.k_var} {var}: {var_type}"

    ## Message constructor
    @staticmethod
    def gen_message_obj(var: str = '') -> str:
        return MurphiTokens.k_message

    ## Integer variable declaration
    @staticmethod
    def gen_int(var: str = '', int_range: str = '') -> str:
        return f"{var}{int_range}"

    ## Boolean variable declaration
    @staticmethod
    def gen_bool(var: str = '') -> str:
        return MurphiTokens.t_bool

    ## Data variable declaration
    @staticmethod
    def gen_data(var: str = '') -> str:
        return MurphiTokens.k_cl_val

    ## ID variable declaration
    @staticmethod
    def gen_id(var: str = ''):
        return MurphiTokens.k_machines

    ## VECTOR variable declaration
    @staticmethod
    def gen_vector(var: str = ''):
        return f"{MurphiTokens.k_vector}{var}"

    ## MULTISET variable declaration
    @staticmethod
    def gen_multiset(var: str = '', set_size: str = '') -> str:
        multi_set =  f"{var}: multiset[{set_size}] of {MurphiTokens.k_machines}{GenPCCToMurphi.gen_end()}"
        return f"{multi_set}{MurphiTokens.k_vector_cnt}{var}: 0..{set_size}{GenPCCToMurphi.gen_end()}"

    ''' Basic object type constructor functions'''
    ## Message object class declaration
    @staticmethod
    def gen_in_message_var(var: str = '') -> str:
        return MurphiTokens.v_in_msg

    @staticmethod
    ## Function to construct a message object
    #  @param msg_obj Message object type (Constructor)
    #  @param msg_type Coherence message type/identifier
    #  @param msg_src Message source
    #  @param msg_dest Message destination
    #  @param payload A list of payload declarations
    def gen_message_constr(msg_obj: str = '', msg_type: str = '', msg_src: str = '', msg_dest: str = '',
                            payload: List[str] = None) -> str:
        msg_constr_str = f"{msg_obj}({MurphiTokens.v_adr}, {msg_type}, {msg_src}, {msg_dest}"
        if payload:
            for entry in payload:
                msg_constr_str += f", {entry}"
        return f"{msg_constr_str})"

    ## Access to message object variable function
    @staticmethod
    def gen_in_message_obj_var_access(var: str = '') -> str:
        return f"{GenPCCToMurphi.gen_in_message_var()}{var}"

    ## Get local machine id function place holder
    @staticmethod
    def gen_get_machine_id_func(var: str = '') -> str:
        return MurphiTokens.v_mach

    ## Get remote machine id function place holder
    @staticmethod
    def gen_get_remote_machine_id_func(var: str = '') -> str:
        return var

    ''' Assignment function place holder declaration '''
    ## Function to generate assignment for values to global variables
    #  @param var Variable to which value is assigned
    #  @param val Value or Variable that get assigned
    @staticmethod
    def gen_assignment(left: str = '', right: str = '') -> str:
        return f"{left} := {right}"

    ## Function to generate access to the value of a global variable
    @staticmethod
    def gen_global_var_val_access(var: str = '') -> str:
        return f"{MurphiTokens.v_cbe}.{var}"

    ## Function to generate access to the value of a global variable
    @staticmethod
    def gen_local_var_val_access(var: str = '') -> str:
        return var

    ## Undefine variable function
    @staticmethod
    def gen_undefine_var(var: str = '') -> str:
        return f"{MurphiTokens.k_undefine} {var}"

    ## Assign next state variables
    #  @param arch_str Name of the architecture, usually including information about level and cluster
    #  @param state_str Coherence state
    @staticmethod
    def gen_next_state(arch_str: str = '', state_str: str = '') -> str:
        next_state_str = f"{MurphiTokens.v_cbe}.{MurphiTokens.k_state} := {arch_str}_{state_str}{GenPCCToBase.end}"
        return next_state_str

    ## RETURN true statement generation
    @staticmethod
    def gen_return_true() -> str:
        return MurphiTokens.k_return + " true"

    ## RETURN false statement generation
    @staticmethod
    def gen_return_false() -> str:
        return MurphiTokens.k_return + " false"

    ''' CONDITION GENERATION'''
    ## IF statement generation
    #  @param left Left condition arg
    #  @param op Operator arg
    #  @param right Right condition arg
    @staticmethod
    def gen_if_func(left: str = '', op: str = '', right: str = '') -> str:
        return f"{MurphiTokens.k_if} ({GenPCCToMurphi.gen_condition(left, op, right)}) " \
               f"{MurphiTokens.k_then}"

    ## IF NOT function place holder (Some languages do not have uniform negation pattern)
    @staticmethod
    def gen_if_not_func(left: str = '', op: str = '', right: str = '') -> str:
        return f"{MurphiTokens.k_if} !({GenPCCToMurphi.gen_condition(left, op, right)}) " \
               f"{MurphiTokens.k_then}"

    ## ELSE statement
    @staticmethod
    def gen_else_func(left: str = '', op: str = '', right: str = '') -> str:
        return f"{MurphiTokens.k_else}"

    ## ELSE
    @staticmethod
    def gen_else_not_func(left: str = '', op: str = '', right: str = '') -> str:
        return f"{MurphiTokens.k_else}"

    ## ENDIF
    @staticmethod
    def gen_end_if_func() -> str:
        return f"{MurphiTokens.k_endif}"

    ## ENDIF
    @staticmethod
    def gen_cond_end_func() -> str:
        GenPCCToMurphi.gen_end_if_func()

    ## Function to convert PCC equal to MURPHI equal
    @staticmethod
    def gen_condition(left: str = '', op: str = '', right: str = '') -> str:
        if op == "==":
            op = "="
        return f"{left} {op} {right}"

    ''' Send functions'''
    ## SEND function place holder
    @staticmethod
    def gen_send_func(vc: str, msg_var: str) -> str:
        return f"{MurphiTokens.k_send_single}{vc}({msg_var}, {MurphiTokens.v_mach})"

    ## MCAST function place holder
    @staticmethod
    def gen_mcast_func(vc: str, multiset: str, msg_var: str, multiset_var: str) -> str:
        return f"{MurphiTokens.k_send_multi}{vc}_{multiset}({msg_var}, {multiset_var}, {MurphiTokens.v_mach})"

    ## BCAST function place holder
    @staticmethod
    def gen_bcast_func(vc: str, cluster: str, msg_var: str) -> str:
        return f"{MurphiTokens.k_send_broad}{vc}_{cluster}({msg_var}, {MurphiTokens.v_mach})"

    ## ISSUE EVENT function, the event must be served by all other local cache blocks
    @staticmethod
    def gen_event_issue_func(arch: str, event: str) -> str:
        return f"{MurphiTokens.k_issue_event}{arch}({arch}_{event}, {MurphiTokens.v_mach}, {MurphiTokens.v_adr})" \
               f"{GenPCCToBase.end}"

    @staticmethod
    def gen_event_handle_func():
        Debug.perror("EVENT HANDLE function not defined")

    ''' Set function place holder declarations'''
    ## SET function place holder
    @staticmethod
    def gen_set_func() -> str:
        Debug.perror("ASSIGNMENT function not defined")

    ## SET ADD function place holder
    @staticmethod
    #  @param set_id Name of the set that needs to perform operation
    #  @param set_op Type of set operation
    #  @param var Name of variable that interacts with set
    def gen_set_add_func(set_id: str = '', set_op: str = '', var: str = '') -> str:
        return GenPCCToMurphi._mod_set_func(set_id, set_op, var)

    ## SET DEL function place holder
    @staticmethod
    def gen_set_del_func(set_id: str = '', set_op: str = '', var: str = '') -> str:
        return GenPCCToMurphi._mod_set_func(set_id, set_op, var)

    ## SET CLEAR function place holder
    @staticmethod
    def gen_set_clear_func(set_id: str = '', set_op: str = '') -> str:
        return GenPCCToMurphi._check_set_func(set_id, set_op)

    ## SET CONTAINS function place holder
    @staticmethod
    def gen_set_contains_func(set_id: str = '', set_op: str = '', var: str = '') -> str:
        return GenPCCToMurphi._mod_set_func(set_id, set_op, var)

    ## SET EMPTY function place holder
    @staticmethod
    def gen_set_empty_func(set_id: str = '', set_op: str = '', var: str = '') -> str:
        return GenPCCToMurphi._mod_set_func(set_id, set_op, var)

    ## SET COUNT function place holder
    @staticmethod
    def gen_set_count_func(set_id: str = '', set_op: str = '') -> str:
        return GenPCCToMurphi._check_set_func(set_id, set_op)

    ## Common helper function for set modifications requiring variable name in set
    @staticmethod
    def _mod_set_func(set_id: str = '', set_op: str = '', var: str = '') -> str:
        return f"{MurphiTokens.k_set_func[set_op]}{set_id}({MurphiTokens.v_cbe}.{set_id}, {var})"

    ## Common helper function for set modification
    @staticmethod
    def _check_set_func(set_id: str = '', set_op: str = '') -> str:
        return f"{MurphiTokens.k_set_func[set_op]}{set_id}({MurphiTokens.v_cbe}.{set_id})"
