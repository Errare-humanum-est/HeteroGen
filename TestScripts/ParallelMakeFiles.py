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

from typing import Dict, List

import sys
import threading
import os
import time

from Backend.Common.TemplateHandler.TemplateHandler import TemplateHandler
from Backend.Murphi.MurphiTemp.TemplateHandler.MurphiTemplates import MurphiTemplates


# Get all litmus test executables
def get_code_files():
    root_path = os.path.abspath(__file__).rsplit('/', 1)[0]
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    for path, _, files in os.walk(root_path):
        for name in files:
            if name.endswith('.m'):
                file_path = os.path.join(path, name)
                litmus_thread_service_list.append(file_path)
    litmus_thread_service_list.sort()
    print("TOTAL NUMBER OF MURPHI FILES: " + str(len(litmus_thread_service_list)))


def progress_report():
    print("Waiting Tests: " + str(len(litmus_thread_service_list)))


# Print how many tests are still pending
def progress_thread_spawn():
    tp = threading.Timer(5.0, progress_report)
    tp.start()
    return tp


def det_max_number_threads() -> int:
    return os.cpu_count()-3


def spawn_threads():
    # Spawn the threads
    for ind in range(0, det_max_number_threads()):
        t = MurphiWorker(ind)
        thread_list.append(t)
        t.start()
        # If too many threads are spawned to fast some workers might terminate with file system access exceptions
        time.sleep(0.5)
    time.sleep(0.1)
    print("Worker thread count: " + str(len(thread_list)))


def print_result():
    print("Compilation Number of Litmus Tests " + str(len(compilation_success_dict.keys())))
    fail_test_count = 0
    failed_test_dict: Dict[str, bool] = {}
    for test_name, outcome in compilation_success_dict.items():
        if not outcome:
            fail_test_count += 1
            failed_test_dict[test_name] = outcome

    if failed_test_dict:
        print("FAIL: The following compilations have failed")
        for key, value in failed_test_dict.items():
            print(key, ' : ', value)
        print(" ")
        print("Number of failed compilations: " + str(fail_test_count))
    else:
        print("SUCCESS: NO ERRORS")


class MurphiWorker(threading.Thread, TemplateHandler):
    def __init__(self, t_id: int):
        threading.Thread.__init__(self)
        TemplateHandler.__init__(self)
        self.t_id = t_id

    def run(self):
        print('Worker Thread ' + str(self.t_id) + ' live')

        queue_full: bool = True
        # Thread continues to service litmus threads
        while queue_full:
            # Acquire queue lock
            thread_lock.acquire()
            if len(litmus_thread_service_list) == 0:
                # Release queue lock for next thread
                thread_lock.release()
                print('Worker Thread ' + str(self.t_id) + ' finished')
                break
            murphi_path = litmus_thread_service_list.pop(0)
            # If too many threads are spawned to fast some workers might terminate with file system access exceptions
            # Runtime of threads is very long, so the 0.2 sec do not hurt performance
            time.sleep(0.2)
            # Release queue lock for next thread
            thread_lock.release()
            murphi_test_name = murphi_path.rsplit('/', 1)[1]

            print("Worker Thread: " + str(self.t_id) + " _:_ " + murphi_test_name)

            # Run Murphi compilation
            self.gen_makefile(murphi_path)

    def gen_makefile(self, murphi_file_path: str):
        os.chdir(murphi_file_path.rsplit('/', 1)[0])
        murphi_file_name = murphi_file_path.rsplit('/', 1)[1].rsplit('.')[0]

        makefile = open("Makefile", "w")
        compaction = "-b"

        replacekeys = [murphi_file_name, compaction]
        template = self._stringReplKeys(self._openTemplate(MurphiTemplates.f_tmp_make), replacekeys)

        makefile.write(template)
        makefile.flush()



# Find all litmus test murphi code files
litmus_thread_service_list: List[str] = []
compilation_success_dict: Dict[str, bool] = {}
get_code_files()

# Spawn the threads
thread_lock = threading.Lock()
thread_list = []
spawn_threads()

# Spawn the progress report thread
progress_thread = progress_thread_spawn()

# Wait for all threads to complete
for t in thread_list:
    t.join()

progress_thread.cancel()

print_result()


