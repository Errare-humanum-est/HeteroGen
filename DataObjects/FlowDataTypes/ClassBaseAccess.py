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
from typing import Union, Dict, List


class Access:
    def __init__(self, name):
        assert isinstance(name, str)
        self.type = name

    def __str__(self):
        return self.type


class Evict:
    def __init__(self, name):
        assert isinstance(name, str)
        self.type = name

    def __str__(self):
        return self.type


class BaseAccess:

    k_load = 'load'
    k_store = 'store'
    k_evict = 'evict'

    # Access keywords
    Access_str_list = [k_load] + [k_store]
    Evict_str_list = [k_evict]

    Access = Access
    Evict = Evict
    Access_type = (Access, Evict)

    def __init__(self):
        self.access_map: Dict[str, Union[Access, Evict]] = {
            self.k_load: Access(self.k_load),
            self.k_store: Access(self.k_store),
            self.k_evict: Evict(self.k_evict)
                                              }
        self.access_to_base_access_map: Dict[Union[Access, Evict], List[Union[Access, Evict, None]]] = {}
        self.map_access_to_base_access(self.k_load, self.k_load)
        self.map_access_to_base_access(self.k_store, self.k_store)
        self.map_access_to_base_access(self.k_evict, self.k_evict)

    def map_access_to_base_access(self, access: str, base_access: Union[str, None]) -> Union[Access, Evict]:

        if base_access in self.Access_str_list:
            access_type = Access(access)
        elif base_access in self.Evict_str_list:
            access_type = Evict(access)
        else:
            # Unknown access
            access_type = Access(access)

        # Generate the new access
        if access not in self.access_map:
            self.access_map[access] = access_type
            if base_access:
                self.access_to_base_access_map[access_type] = [self.access_map[base_access]]
            else:
                self.access_to_base_access_map[access_type] = [None]
        else:
            access_type = self.access_map[access]
            if base_access in self.access_map:
                if self.access_map[base_access] in self.access_to_base_access_map:
                    self.access_to_base_access_map[access_type].append(self.access_map[base_access])
                else:
                    self.access_to_base_access_map[access_type] = [self.access_map[base_access]]

        return access_type

    def copy_base_access(self) -> 'BaseAccess':
        new_base_access = BaseAccess()
        new_base_access.merge_base_access(self)
        return new_base_access

    def merge_base_access(self, other: 'BaseAccess'):
        self.access_map.update(other.access_map)
        self.access_to_base_access_map.update(other.access_to_base_access_map)

    def update_base_access(self, other):
        self.access_to_base_access_map.update(other.access_to_base_access_map)
