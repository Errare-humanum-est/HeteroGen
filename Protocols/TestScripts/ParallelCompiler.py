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

from typing import Dict, List, Union

import sys
import threading
import os
import time
import re
import subprocess


# Get all litmus test executables
def get_code_files(root_path: str = ''):
    if not root_path:
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
    return os.cpu_count()-1


def spawn_threads():
    # Spawn the threads
    for ind in range(0, det_max_number_threads()):
        t = MurphiWorkerThread(ind)
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
    for test_path, outcome in compilation_success_dict.items():
        test_name = test_path.rsplit('/', 1)[1]
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


class MurphiWorkerThread(threading.Thread):
    def __init__(self, t_id: int):
        threading.Thread.__init__(self)
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

            # Run Murphi compilation
            self.run_compilation(murphi_path)

    @staticmethod
    def update_murphi_file(murphi_dir_path: str):
        makefile_str = MurphiWorkerThread.read_file(murphi_dir_path, 'Makefile')

        if '$2$' in makefile_str:
            makefile_str = re.sub('\$2\$', murphi_compiler_path, makefile_str)

        MurphiWorkerThread.write_file(murphi_dir_path, 'Makefile', makefile_str)

    def run_compilation(self, murphi_file_path: str):
        murphi_dir_path = murphi_file_path.rsplit('/', 1)[0]
        murphi_test_name = murphi_file_path.rsplit('/', 1)[1]
        print("Worker Thread: " + str(self.t_id) + " _:_ " + murphi_test_name)
        self.update_murphi_file(murphi_dir_path)

        compile_report = self.run_subprocess_cmd(murphi_dir_path, ['make'])

        self.write_file(murphi_dir_path, murphi_file_path.rsplit(".", 1)[0] + "_compile" + ".txt", compile_report)

        # Report the result
        res = re.search(r'Makefile:[\w\s:]*\'[\w\s.]*\'\s*failed', compile_report)
        thread_lock.acquire()
        if res:
            compilation_success_dict[murphi_file_path] = False
        compilation_success_dict[murphi_file_path] = True
        thread_lock.release()

    @staticmethod
    def run_subprocess_cmd(exe_path: str, cmd_list: List[str]) -> str:
        linux_io_lock.acquire()
        time.sleep(0.3)
        os.chdir(exe_path)
        linux_io_lock.release()
        # Run subprocess and wait for it to complete
        report = subprocess.run(cmd_list, stdout=subprocess.PIPE).stdout.decode("utf-8")
        return report

    @staticmethod
    def file_exists(murphi_path: str):
        linux_io_lock.acquire()
        time.sleep(0.1)
        ret_bool = os.path.isfile(murphi_path)
        linux_io_lock.release()
        return ret_bool

    @staticmethod
    def read_file(exe_path: str, file_name: str) -> Union[None, str]:
        linux_io_lock.acquire()

        # Change the directory path
        time.sleep(0.1)
        os.chdir(exe_path)

        # If file is returned by other function, then the file is closed, odd behaviour
        file = None
        retry_count: int = 5

        for ind in range(0, retry_count):
            try:
                file = open(file_name, 'r')
                if file:
                    break
            except:
                time.sleep(ind + 1)

        # If file does not exist return None
        if not file:
            linux_io_lock.release()
            return None

        # Read string from file and close file
        try:
            makefile_str = file.read()
        except:
            linux_io_lock.release()
            return None

        time.sleep(0.1)
        file.close()
        linux_io_lock.release()
        return makefile_str

    @staticmethod
    def write_file(exe_path: str, file_name: str, report: str) -> bool:
        linux_io_lock.acquire()

        # Change the directory path
        time.sleep(0.1)
        os.chdir(exe_path)

        # If file is returned by other function, then the file is closed, odd behaviour
        file = None
        retry_count: int = 5

        for ind in range(0, retry_count):
            try:
                file = open(file_name, 'w')
                if file:
                    break
            except:
                time.sleep(ind + 1)

        # If file does not exist return False
        if not file:
            linux_io_lock.release()
            return False

        # Write string to file and close file
        try:
            file.write(report)
        except:
            linux_io_lock.release()
            return False

        time.sleep(0.1)
        file.close()
        linux_io_lock.release()
        return True


def_path = os.getcwd()

# PATH TO THE MURPHI VARIABLE
murphi_compiler_path = '/home/tux/Desktop/murphi'
litmus_test_files_path = def_path + '/../MOESI_Directory/RF_Dir/ord_net/HeteroGen'

# Find all litmus test murphi code files
litmus_thread_service_list: List[str] = []
compilation_success_dict: Dict[str, bool] = {}
get_code_files(litmus_test_files_path)

# Lock for shared data
thread_lock = threading.Lock()
# Lock for linux system calls and file accesses, to avoid linux io errors
linux_io_lock = threading.Lock()
thread_list = []

# Spawn the threads
spawn_threads()

# Spawn the progress report thread
progress_thread = progress_thread_spawn()

# Wait for all threads to complete
for t in thread_list:
    t.join()

progress_thread.cancel()

print_result()

