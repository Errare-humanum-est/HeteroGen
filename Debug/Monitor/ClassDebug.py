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

from colorama import init, Fore, Style
from tabulate import tabulate

from typing import List


class Debug:

    spacer = "\n\n\n"

    def __init__(self, debug_enabled: bool = False):

        self.dbg: bool = debug_enabled

    def p_header(self, header: str = '', show: bool = False):
        if self.dbg or show:
            print(Fore.LIGHTBLUE_EX + header + Style.RESET_ALL)

    def pdebug(self, debug: str = ''):
        if self.dbg:
            print(debug)

    def pdebugwarning(self, warning: str = ''):
        if self.dbg:
            print(Fore.YELLOW + warning + Style.RESET_ALL)

    @ staticmethod
    def psection(section_name: str = ''):
        print(Fore.CYAN + section_name + Style.RESET_ALL)

    @staticmethod
    def ptext(text: str = ''):
        print(text)

    @ staticmethod
    def pwarning(warning: str = '', cond: bool = True):
        if cond:
            print(Fore.MAGENTA + "warning: " + warning + Style.RESET_ALL)

    @ staticmethod
    def perror(error: str = '', cond=0):
        error = Fore.RED + error + Style.RESET_ALL
        if not cond:
            print('Pause')
        assert cond, error

    @ staticmethod
    def psuccess(successmsg: str = ''):
        print(Fore.GREEN + successmsg + Style.RESET_ALL)

    def ptable(self, header: List[str], body: List[List[str]]):
        if self.dbg:
            assert isinstance(header, list) and isinstance(body, list)

            for ind in range(0, len(header)):
                header[ind] = Fore.GREEN + header[ind]

                if ind == len(header)-1:
                    header[ind] += Style.RESET_ALL

            print(tabulate(body, headers=header))
