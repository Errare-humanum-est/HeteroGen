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

#
#
#

from typing import Tuple, Union

from DataObjects.ClassState import State
from DataObjects.ClassTrace import Trace


class StateTuple:

    def __init__(self, ll_cc: [State, Trace, None] = None,
                 ll_dir: [State, Trace, None] = None,
                 ll_rm: [State, Trace, None] = None,
                 prev_tuple: 'StateTuple' = None):

        self.prev_tuple = prev_tuple

        self.ll_cc_start_state: State = None
        self.ll_cc_final_state: State = None
        self.ll_cc_trace: Trace = None

        self.ll_rm_start_state: State = None
        self.ll_rm_final_state: State = None
        self.ll_rm_trace: Trace = None

        self.ll_dir_start_state: State = None
        self.ll_dir_final_state: State = None
        self.ll_dir_trace: Trace = None

        self.update_ll_cc(ll_cc)
        self.update_ll_rm(ll_rm)
        self.update_ll_dir(ll_dir)

        self.safe = 1   # A closed chain was found

    def __str__(self):
        retstr = self._str_cond(self.ll_cc_start_state, self.ll_cc_final_state, self.ll_cc_trace) + "; "
        retstr += self._str_cond(self.ll_rm_start_state, self.ll_rm_final_state, self.ll_rm_trace) + "; "
        retstr += self._str_cond(self.ll_dir_start_state, self.ll_dir_final_state, self.ll_dir_trace)
        return retstr

    @staticmethod
    def _str_cond(start_state, end_state, trace) -> str:
        if trace:
            str_trace = ""
            for node in trace.trace:
                if not node.transition:
                    str_trace += str(node.state) + " --> "
            return str_trace + str(end_state)

        else:
            if start_state != end_state:
                return str(start_state) + " --> " + str(end_state)
            else:
                return str(end_state)

    def __hash__(self):
        return hash((self.ll_cc_start_state, self.ll_cc_final_state, self.ll_cc_trace,
                     self.ll_rm_start_state, self.ll_rm_final_state, self.ll_rm_trace,
                     self.ll_dir_start_state, self.ll_dir_final_state, self.ll_dir_trace))

    def sym_red_eq(self, other: 'StateTuple') -> bool:
        if self.__eq__(other) or self.__sym__eq__(other):
            return True
        return False

    def __eq__(self, other: 'StateTuple'):
        if isinstance(other, StateTuple):
            if self.ll_cc_start_state == other.ll_cc_start_state and \
                    self.ll_cc_final_state == other.ll_cc_final_state and \
                    self.ll_cc_trace == other.ll_cc_trace and \
                    \
                    self.ll_rm_start_state == other.ll_rm_start_state and \
                    self.ll_rm_final_state == other.ll_rm_final_state and \
                    self.ll_rm_trace == other.ll_rm_trace and \
                    \
                    self._dir_eq(self, other):
                return True
        return False

    def __sym__eq__(self, other: 'StateTuple') -> bool:
        if isinstance(other, StateTuple):
            if self._sym_eq_check(self, other) and self._sym_eq_check(other, self) and self._dir_eq(self, other):
                return True
        return False

    @staticmethod
    def _dir_eq(_self: 'StateTuple', _other: 'StateTuple') -> bool:
        if _self.ll_dir_start_state == _other.ll_dir_start_state and \
                _self.ll_dir_final_state == _other.ll_dir_final_state and \
                _self.ll_dir_trace == _other.ll_dir_trace:
            return True
        return False

    @ staticmethod
    def _sym_eq_check(_self: 'StateTuple', _other: 'StateTuple') -> bool:
        if _self.ll_cc_start_state == _other.ll_rm_start_state and \
                _self.ll_cc_final_state == _other.ll_rm_final_state and \
                _self.ll_cc_trace == _other.ll_rm_trace:
            return True
        return False

    def update_ll_cc(self, ll_cc: [State, Trace]):
        if isinstance(ll_cc, State):
            self.ll_cc_start_state = ll_cc
            self.ll_cc_final_state = ll_cc
        elif isinstance(ll_cc, Trace):
            self.ll_cc_start_state = ll_cc.startstate
            self.ll_cc_final_state = ll_cc.finalstate
            self.ll_cc_trace = ll_cc
        else:
            assert "Unknown data type @ ll_cc"

    def update_ll_rm(self, ll_cc: [State, Trace]):
        if isinstance(ll_cc, State):
            self.ll_rm_start_state = ll_cc
            self.ll_rm_final_state = ll_cc
        elif isinstance(ll_cc, Trace):
            self.ll_rm_start_state = ll_cc.startstate
            self.ll_rm_final_state = ll_cc.finalstate
            self.ll_rm_trace = ll_cc
        else:
            assert "Unknown data type @ ll_cc_dir"

    def update_ll_dir(self, ll_dir: [State, Trace]):
        if isinstance(ll_dir, State):
            self.ll_dir_start_state = ll_dir
            self.ll_dir_final_state = ll_dir
        elif isinstance(ll_dir, Trace):
            self.ll_dir_start_state = ll_dir.startstate
            self.ll_dir_final_state = ll_dir.finalstate
            self.ll_dir_trace = ll_dir
        else:
            assert "Unknown data type @ ll_dir"

    def get_access_trace(self) -> Union[Trace, None]:
        if self.ll_cc_trace:
            if self.ll_cc_trace.access:
                return self.ll_cc_trace
        if self.ll_rm_trace:
            if self.ll_rm_trace.access:
                return self.ll_rm_trace
        return None

    # Create symmetric copy
    def get_symmetric_copy_args(self):
        return self.get_ll_rm(), self.get_ll_dir(), self.get_ll_cc(), self.prev_tuple

    def get_ll_cc(self) -> Union[State, Trace]:
        if self.ll_cc_trace:
            return self.ll_cc_trace
        else:
            return self.ll_cc_final_state

    def get_ll_rm(self) -> Union[State, Trace]:
        if self.ll_rm_trace:
            return self.ll_rm_trace
        else:
            return self.ll_rm_final_state

    def get_ll_dir(self) -> Union[State, Trace]:
        if self.ll_dir_trace:
            return self.ll_dir_trace
        else:
            return self.ll_dir_final_state

    # Return state set of system, set is required because of symmetry
    def get_ll_cc_state_set_str(self) -> str:
        str_list = [str(self.ll_cc_final_state), str(self.ll_rm_final_state)]
        str_list.sort()
        return "; ".join(str_list)

    def update_prev_tuple(self, prev_tuple: 'StateTuple'):
        self.prev_tuple = prev_tuple

    def test_complete(self) -> int:
        if self.ll_cc_final_state and self.ll_cc_trace and self.ll_dir_final_state and self.ll_dir_trace and \
                self.ll_rm_start_state and self.ll_rm_trace:
            return 1
        return 0

    def raw_data_cc_rm_dir(self) -> Tuple[Union[State, Trace], Union[State, Trace], Union[State, Trace]]:
        return self.get_ll_cc(), self.get_ll_rm(), self.get_ll_dir()

    # Drawing
    def str_start_state(self) -> str:
        return str(self.ll_cc_start_state) + "; " + str(self.ll_rm_start_state) + "; " + str(self.ll_dir_start_state)

    def str_final_state(self) -> str:
        return str(self.ll_cc_final_state) + "; " + str(self.ll_rm_final_state) + "; " + str(self.ll_dir_final_state)

    def str_access_trace(self) -> str:
        if self.ll_cc_trace:
            if self.ll_cc_trace.access:
                return "cc_" + ", ".join(self.ll_cc_trace.access)
        if self.ll_rm_trace:
            if self.ll_rm_trace.access:
                return "rm_" + ", ".join(self.ll_rm_trace.access)

    def symmetric_str_start_state(self) -> str:
        # Return state set of system, set is required because of symmetry
        str_list = [str(self.ll_cc_start_state), str(self.ll_rm_start_state)]
        str_list.sort()
        return "; ".join(str_list) + "; " + str(self.ll_dir_start_state)

    def symmetric_str_final_state(self) -> str:
        # Return state set of system, set is required because of symmetry
        str_list = [str(self.ll_cc_final_state), str(self.ll_rm_final_state)]
        str_list.sort()
        return "; ".join(str_list) + "; " + str(self.ll_dir_final_state)

    def symmetric_str_access_trace(self) -> str:
        if self.ll_cc_trace:
            if self.ll_cc_trace.access:
                return ", ".join(self.ll_cc_trace.access)
        if self.ll_rm_trace:
            if self.ll_rm_trace.access:
                return ", ".join(self.ll_rm_trace.access)
