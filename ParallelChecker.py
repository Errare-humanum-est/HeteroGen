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
from psutil import virtual_memory
import subprocess
import re


# Get all litmus test executables
def get_executables(root_path: str = ''):
    if not root_path:
        root_path = os.path.abspath(__file__).rsplit('/', 1)[0]
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    for path, _, files in os.walk(root_path):
        for name in files:
            file_path = os.path.join(path, name)
            if os.access(file_path, os.X_OK):
                litmus_test_dict[file_path] = def_memory
                litmus_test_result_dict[file_path] = k_not_served
    print("Total number of Murphi Test files: " + str(len(litmus_test_dict)))


# Determine threads that are ready to run next
def gen_exec_thread_list() -> bool:
    if not litmus_test_dict:
        print('No murphi tests found')
        return False

    min_mem = def_memory
    for litmus_test_path in litmus_test_dict:
        thread_count_list = re.findall('_nM\d+', litmus_test_path.rsplit('/', 1)[1])
        if len(thread_count_list) == 1:
            thread_count = re.findall('\d+', thread_count_list[0])[0]
            if thread_count in k_machines:
                litmus_test_dict[litmus_test_path] = k_machines[thread_count]
                min_mem = min(min_mem, k_machines[thread_count])

    # Check if the minimum amount of memory required at least one of the tests is available
    free_mem_count = (int(virtual_memory().free / 2 ** 20) - min_free_sys_memory)
    if free_mem_count < min_mem:
        print('Not enough free memory available to run Murphi tests')
        return False

    global litmus_thread_service_list
    litmus_thread_service_list = [test_path[0]
                                  for test_path in sorted(list(litmus_test_dict.items()), key=lambda x: x[1])]

    return True


def det_max_number_threads(mem: int = 0) -> int:
    cpu_count = os.cpu_count() - 1
    return cpu_count
    #mem_cpu_count = int((int(virtual_memory().free / 2 ** 20) - 8000) / mem)
    #return min(cpu_count, mem_cpu_count)


def spawn_threads():
    print("Spawning worker threads")
    # Spawn the threads
    for ind in range(0, det_max_number_threads()):
        work_thread = MurphiWorkerThread(ind)
        thread_list.append(work_thread)
        work_thread.start()
        # If too many threads are spawned to fast some workers might terminate with file system access exceptions
        time.sleep(0.5)
    time.sleep(0.1)
    print("Worker thread count: " + str(len(thread_list)))

    # Start the progress thread
    prog_thread = ProgressThread()
    prog_thread.start()


def print_result():
    result_str = "Executed Number of Litmus Tests " + str(len(litmus_test_dict.keys())) + '\n'
    failed_test_dict = {}
    passed_test_dict = {}
    for test_name, outcome in litmus_test_result_dict.items():
        if outcome == k_pass:
            passed_test_dict[test_name] = outcome
        elif outcome != k_not_served:
            failed_test_dict[test_name] = outcome

    if failed_test_dict:
        result_str += "FAILS: The following tests have failed" + '\n'
        for key, value in failed_test_dict.items():
            result_str += str(key) + ' : ' + str(value) + '\n'
        result_str += '\n'
        result_str += "Number of failed tests: " + str(len(failed_test_dict)) + '\n'
        print(result_str)

    if passed_test_dict:
        result_str += "SUCCESS: The following tests have passed" + '\n'
        for key, value in passed_test_dict.items():
            result_str += str(key) + ' : ' + str(value) + '\n'
        result_str += '\n'
        result_str += "Number of passed tests: " + str(len(passed_test_dict)) + '\n'

    result_str += "Waiting not scheduled Tests: " + str(len(litmus_thread_service_list)) + '\n'

    if not failed_test_dict and len(litmus_thread_service_list) == 0:
        result_str += "SUCCESS: No Errors" + '\n'

    MurphiWorkerThread.write_file(def_path, 'TestScripts/Test_Result.txt', result_str)

    if len(litmus_thread_service_list) == 0:
        print(result_str)


# Progress thread report
class ProgressThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.result_auto_save_counter = 0

    def run(self):
        while report_thread_enabled:
            print("Waiting not scheduled Tests: " + str(len(litmus_thread_service_list)))
            time.sleep(30.0)
            for test, result in litmus_test_result_dict.items():
                if result in k_fail_list:
                    print("Failed Test " + str(test) + " : " + str(result))

            self.result_auto_save_counter += 1
            if self.result_auto_save_counter >= 10:
                self.result_auto_save_counter = 0
                # Regularly save intermediate results
                print_result()


# Murphi worker thread
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
                time.sleep(0.1)
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

            # Run Murphi verification
            self.run_murphi(murphi_path)

    def run_murphi(self, murphi_path: str):
        if self.file_exists(murphi_path):
            # Wait for memory to become free
            while self.get_free_mem() < litmus_test_dict[murphi_path]:
                print('Worker Thread ' + str(self.t_id) + ': Waiting for free memory')
                time.sleep(10)

            # Run executable
            murphi_dir_path = murphi_path.rsplit('/', 1)[0]
            murphi_test_name = murphi_path.rsplit('/', 1)[1]
            print("Worker Thread: " + str(self.t_id) + " _:_ " + murphi_test_name)
            # Run Murphi executable & generate report file
            cmd = ["./" + murphi_test_name, "-tv", "-pr", "-m", str(litmus_test_dict[murphi_path])]
            report = self.run_subprocess_cmd(murphi_dir_path, cmd)

            # Safe the report file atomically
            self.write_file(murphi_dir_path, murphi_test_name + "_results" + ".txt", report)

            # Update the result
            thread_lock.acquire()
            if ('Closed hash table full' in report or 'Too many active states' in report or
                    ('Status' not in report and 'Result' not in report)):
                # Check if the error is out of memory, if yes, then do not reschedule thread
                litmus_test_dict[murphi_path] = self.calc_next_mem(litmus_test_dict[murphi_path])
                if isinstance(litmus_test_dict[murphi_path], int):
                    # Insert at head, because longer litmus test need longer to compute
                    if smallest_first:
                        litmus_thread_service_list.append(murphi_path)
                    else:
                        litmus_thread_service_list.insert(0, murphi_path)
                    print('Reschedule ' + str(murphi_test_name) + ' as previous check ran out of memory')
                else:
                    litmus_test_result_dict[murphi_path] = k_oom

            elif k_dead in report:
                litmus_test_result_dict[murphi_path] = k_dead
            elif k_invariant in report:
                litmus_test_result_dict[murphi_path] = k_invariant
            elif "Litmus Test Failed" in report:
                litmus_test_result_dict[murphi_path] = k_litmus_fail
            elif "No error found" not in report:
                litmus_test_result_dict[murphi_path] = k_fail
            else:
                litmus_test_result_dict[murphi_path] = k_pass
                print("PASSED: Worker Thread: " + str(self.t_id) + " _:_ " + murphi_test_name)

            thread_lock.release()

        else:
            print("Unable to locate executable file in path: " + murphi_path)
            litmus_test_result_dict[murphi_path] = k_not_found


    @staticmethod
    def run_subprocess_cmd(exe_path: str, cmd_list: List[str]) -> str:
        linux_io_lock.acquire()
        time.sleep(0.3)
        os.chdir(exe_path)
        linux_io_lock.release()
        try:
            # Run subprocess and wait for it to complete
            report = subprocess.run(cmd_list, stdout=subprocess.PIPE).stdout.decode("utf-8")
        except:
            return ''

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
        time.sleep(0.1)

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

        time.sleep(0.1)

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

        time.sleep(0.2)
        file.close()
        time.sleep(0.2)
        linux_io_lock.release()
        return makefile_str

    @staticmethod
    def write_file(exe_path: str, file_name: str, report: str) -> bool:
        linux_io_lock.acquire()

        # Change the directory path
        time.sleep(0.1)
        os.chdir(exe_path)
        time.sleep(0.1)

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

        time.sleep(0.1)

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

        time.sleep(0.2)
        file.close()
        time.sleep(0.2)
        linux_io_lock.release()
        return True

    @staticmethod
    def get_free_mem() -> int:
        mem_check_lock.acquire()
        time.sleep(0.1)
        free_mem = int(virtual_memory().free / 2 ** 20) - min_free_sys_memory
        mem_check_lock.release()
        return free_mem

    @staticmethod
    def calc_next_mem(mem: int) -> Union[int, str]:
        if mem < max_memory:
            new_mem = mem * 2
            if new_mem < max_memory:
                return new_mem
            else:
                return max_memory
        else:
            return k_oom


# Murphi results
k_not_served = 'Not served yet'
k_pass = 'Pass'
k_fail = 'Fail'
k_litmus_fail = 'Litmus test fail'
k_dead = 'Deadlock'
k_invariant = 'Invariant'
k_oom = 'Out of memory'
k_not_found = 'File not found'

k_fail_list = [k_fail, k_litmus_fail, k_dead, k_not_found]


# Minimum system memory that is kept free
min_free_sys_memory = 4000
# Machine count memory assignment suggestions
k_machines = {1: 4000,
              2: 4000,
              3: 4000,
              4: 8000,
              5: 32000}
# Default thread memory if not thread count is provided
def_memory = 4000
# Maximum amount of memory a litmus test can allocate
#max_memory = virtual_memory().free
max_memory = 64000

# Record the default path to dump result file into
def_path = os.getcwd()

litmus_test_files_path = def_path + '/Protocols/MOESI_Directory/RF_Dir/ord_net/HeteroGen'

# Runs smallest litmus tests first
smallest_first = True

# Find all litmus test executables
# Dict of all litmus tests and amount of memory allocated for first run
litmus_test_dict: Dict[str, Union[str, int]] = {}
# List of pending litmus tests
litmus_thread_service_list: List[str] = []
# Dict reporting the litmus test results
litmus_test_result_dict: Dict[str, str] = {}


# Get all Murphi executables in sub_folders or path
get_executables(litmus_test_files_path)

# Spawn the threads
# Lock for linux system calls and file accesses, to avoid linux io errors
linux_io_lock = threading.Lock()
# Check free memory lock
mem_check_lock = threading.Lock()
# Lock for shared data
thread_lock = threading.Lock()

thread_list = []

litmus_test_valid = gen_exec_thread_list()

report_thread_enabled = True

while litmus_test_valid:

    if not litmus_thread_service_list:
        break

    print("Starting new model checking run")

    # Spawn the worker threads and the progress thread
    spawn_threads()

    if not thread_list:
        print('Unable to launch threads, not enough memory and system resources free (min 4GB RAM)')
        break

    # Wait for all threads to complete
    for t in thread_list:
        t.join()

    report_thread_enabled = False

print_result()


