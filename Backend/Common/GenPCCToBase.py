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

from Debug.Monitor.ClassDebug import Debug
from Backend.Common.TemplateHandler.TemplateBase import TemplateBase


class GenPCCToBase(TemplateBase):

    k_if = 'IF_'
    k_else = 'ELSE_'
    k_endif = 'ENDIF_'
    k_state = 'STATE_'

    set_func_sel = {
        "add": "gen_set_add_func",
        "del": "gen_set_del_func",
        "clear": "gen_set_clear_func",
        "contains": "gen_set_contains_func",
        "empty": "gen_set_empty_func",
        "count": "gen_set_count_func"
    }

    def __init__(self):
        TemplateBase.__init__(self)

    def __str__(self):
        return self.__name__

    ''' General functions '''
    ## New line placeholder
    @staticmethod
    def gen_nl():
        Debug.perror("NEWLINE function not defined")

    ## End statement placeholder
    @staticmethod
    def gen_end():
        Debug.perror("END STATEMENT function not defined")

    ''' Variable declarations '''
    ## Variable declaration function place holder
    @staticmethod
    def gen_var_decl_func(var: str = '', var_type: str = '', val: str = ''):
        Debug.perror("VARIABLE DECLARATION function not defined")

    ## Message constructor place holder
    @staticmethod
    def gen_message_obj(var: str = ''):
        Debug.perror('MESSAGE OBJECT function not defined')

    ## Integer variable declaration
    @staticmethod
    def gen_int(var: str = '', int_range: str = ''):
        Debug.perror('INT declaration function not defined')

    ## Boolean variable declaration
    @staticmethod
    def gen_bool(var: str = ''):
        Debug.perror('BOOL declaration function not defined')

    ## Data variable declaration
    @staticmethod
    def gen_data(var: str = ''):
        Debug.perror('DATA declaration function not defined')

    ## ID variable declaration
    @staticmethod
    def gen_id(var: str = ''):
        Debug.perror('ID declaration function not defined')

    ## MULTISET variable declaration
    @staticmethod
    def gen_vector(var: str = ''):
        Debug.perror('MULTISET declaration function not defined')

    ## MULTISET variable declaration
    @staticmethod
    def gen_multiset(var: str = ''):
        Debug.perror('MULTISET declaration function not defined')

    ''' Basic object type constructor functions'''
    ## Message in message var place holder
    @staticmethod
    def gen_in_message_var(var: str = ''):
        Debug.perror("IN-MESSAGE Variable function not defined")

    @staticmethod
    ## Message object constructor place holder
    #  @param msg_obj Message object type (Constructor)
    #  @param msg_type Coherence message type/identifier
    #  @param msg_src Message source
    #  @param msg_dest Message destination
    #  @param payload A list of payload declarations
    def gen_message_constr(msg_obj: str = '', msg_type: str = '', msg_src: str = '', msg_dest: str = '',
                         payload: List[str] = None):
        Debug.perror("MESSAGE CONSTRUCTOR function not defined")

    ## Access to message object variable function place holder
    @staticmethod
    def gen_in_message_obj_var_access(var: str = ''):
        Debug.perror("MESSAGE OBJECT VAR ACCESS function not defined")

    ## Get local machine id function place holder
    @staticmethod
    def gen_get_machine_id_func(var: str = ''):
        Debug.perror("GET MACHINE ID function not defined")

    ## Get remote machine id function place holder
    @staticmethod
    def gen_get_remote_machine_id_func(var: str = ''):
        Debug.perror("GET REMOTE MACHINE ID function not defined")

    ''' Assignment function place holder declaration '''
    ## Function to generate assignment for variables and values
    #  @param left Variable to which value is assigned
    #  @param right Value or Variable that get assigned
    @staticmethod
    def gen_assignment(left: str = '', right: str = ''):
        Debug.perror("ASSIGNMENT function not defined")

    ## Function to generate access to the value of a global variable
    @staticmethod
    def gen_global_var_val_access(var: str = ''):
        Debug.perror("GLOBAL VAR ACCESS function not defined")

    ## Function to generate access to the value of a global variable
    @staticmethod
    def gen_local_var_val_access(var: str = ''):
        Debug.perror("LOCAL VAR ACCESS function not defined")

    ## Undefine variable function place holder
    @staticmethod
    def gen_undefine_var(var: str = ''):
        Debug.perror("VAR UNDEFINE function not defined")

    ## Assign next state variables
    @staticmethod
    def gen_next_state(arch_str: str = '', state_str: str = ''):
        Debug.perror("STATE ASSIGNMENT function not defined")

    ''' Conditional function place holder declarations'''
    ## IF function place holder
    #  @param self The object pointer.
    #  @param left Left condition arg
    #  @param op Operator arg
    #  @param right Right condition arg
    @staticmethod
    def gen_if_func(left: str = '', op: str = '', right: str = ''):
        Debug.perror("IF function not defined")

    ## IF NOT function place holder (Some languages do not have uniform negation pattern)
    @staticmethod
    def gen_if_not_func(left: str = '', op: str = '', right: str = ''):
        Debug.perror("IF NOT function not defined")

    @staticmethod
    ## ELSE function place holder
    def gen_else_func(left: str = '', op: str = '', right: str = ''):
        Debug.perror("ELSE function not defined")

    @staticmethod
    ## ELSE NOT function place holder (Some languages do not have else statement so negation required)
    def gen_else_not_func(left: str = '', op: str = '', right: str = ''):
        Debug.perror("ELSE NOT function not defined")

    ## ENDIF function place holder
    @staticmethod
    def gen_end_if_func():
        Debug.perror("ENDIF function not defined")

    # Legacy
    @staticmethod
    def gen_cond_end_func():
        GenPCCToBase.gen_end_if_func()

    ''' Send functions'''
    ## SEND function place holder
    @staticmethod
    def gen_send_func(vc: str, msg_var: str):
        Debug.perror("SEND function not defined")

    ## MCAST function place holder
    @staticmethod
    def gen_mcast_func(vc: str, multiset: str, msg_var: str, multiset_var: str):
        Debug.perror("MCAST function not defined")

    ## BCAST function place holder
    @staticmethod
    def gen_bcast_func(vc: str, cluster: str, msg_var: str):
        Debug.perror("BCAST function not defined")

    ## ISSUE EVENT function place holder
    @staticmethod
    def gen_event_issue_func(arch: str, event: str):
        Debug.perror("EVENT CALL function not defined")

    @staticmethod
    def gen_event_handle_func():
        Debug.perror("EVENT HANDLE function not defined")

    @staticmethod
    def gen_event_wait_handled_func():
        Debug.perror("EVENT WAIT HANDLED function not defined")

    @staticmethod
    def gen_access_func():
        Debug.perror("ACCESS function not defined")

    @staticmethod
    def gen_break_func():
        Debug.perror("BREAK function not defined")

    @staticmethod
    def gen_undef_func():
        Debug.perror("UNDEFINE function not defined")

    # Legacy
    @staticmethod
    def gen_end_proc_func():
        Debug.perror("ENDPROCESS function not defined")

    @staticmethod
    def gen_end_when_func():
        Debug.perror("ENDPROCESS function not defined")


    ''' Set function place holder declarations'''
    ## SET function place holder
    @staticmethod
    def gen_set_func():
        Debug.perror("ASSIGNMENT function not defined")

    ## SET ADD function place holder
    @staticmethod
    def gen_set_add_func(set_id: str = '', set_op: str = '', var: str = ''):
        Debug.perror("SET ADD function not defined")

    ## SET DEL function place holder
    @staticmethod
    def gen_set_del_func(set_id: str = '', set_op: str = '', var: str = ''):
        Debug.perror("SET DEL function not defined")

    ## SET CLEAR function place holder
    @staticmethod
    def gen_set_clear_func(set_id: str = '', set_op: str = ''):
        Debug.perror("SET CLEAR function not defined")

    ## SET CONTAINS function place holder
    @staticmethod
    def gen_set_contains_func(set_id: str = '', set_op: str = '', var: str = ''):
        Debug.perror("SET CONTAINS function not defined")

    ## SET EMPTY function place holder
    @staticmethod
    def gen_set_empty_func(set_id: str = '', set_op: str = '', var: str = ''):
        Debug.perror("SET EMPTY function not defined")

    ## SET COUNT function place holder
    @staticmethod
    def gen_set_count_func(set_id: str = '', set_op: str = ''):
        Debug.perror("SET COUNT function not defined")
