import multiprocessing
import time
import os
import signal
import sys
import traceback
import re
import filecmp
import argparse
import inspect
import asyncio

import stateManager
import studentAPI
import Ansible
import runtime_pb2

from runtimeUtil import *

ALL_PROCESSES = {}


# pylint: disable=too-many-branches
def runtime(test_name=""): # pylint: disable=too-many-statements
    test_mode = test_name != ""
    max_iter = 3 if test_mode else None

    def non_test_mode_print(*args):
        """Prints only if we are NOT in test_mode"""
        if not test_mode:
            print(args)

    bad_things_queue = multiprocessing.Queue()
    state_queue = multiprocessing.Queue()
    spawn_process = process_factory(bad_things_queue, state_queue)
    restart_count = 0
    emergency_stopped = False

    try:
        spawn_process(PROCESS_NAMES.STATE_MANAGER, start_state_manager)
        spawn_process(PROCESS_NAMES.UDP_RECEIVE_PROCESS, start_udp_receiver)
        spawn_process(PROCESS_NAMES.HIBIKE, start_hibike)
        control_state = "idle"
        dawn_connected = False

        while True:
            if test_mode:
                # Automatically enter telop mode when running tests
                bad_things_queue.put(
                    BadThing(
                        sys.exc_info(),
                        "Sending initial command to enter teleop",
                        event=BAD_EVENTS.ENTER_TELEOP,
                        printStackTrace=False))
            if restart_count >= 3:
                non_test_mode_print(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
                non_test_mode_print("Too many restarts, terminating")
                break
            if emergency_stopped:
                non_test_mode_print(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
                non_test_mode_print("terminating due to E-Stop")
                break
            non_test_mode_print(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
            non_test_mode_print("Starting studentCode attempt: %s" % (restart_count,))
            while True:
                new_bad_thing = bad_things_queue.get(block=True)
                if new_bad_thing.event == BAD_EVENTS.NEW_IP and not dawn_connected:
                    spawn_process(PROCESS_NAMES.UDP_SEND_PROCESS, start_udp_sender)
                    spawn_process(PROCESS_NAMES.TCP_PROCESS, start_tcp)
                    dawn_connected = True
                    continue
                elif new_bad_thing.event == BAD_EVENTS.DAWN_DISCONNECTED and dawn_connected:
                    terminate_process(PROCESS_NAMES.UDP_RECEIVE_PROCESS)
                    terminate_process(PROCESS_NAMES.UDP_SEND_PROCESS)
                    terminate_process(PROCESS_NAMES.TCP_PROCESS)
                    spawn_process(PROCESS_NAMES.UDP_RECEIVE_PROCESS, start_udp_receiver)
                    dawn_connected = False
                    control_state = "idle"
                    break
                elif new_bad_thing.event == BAD_EVENTS.ENTER_TELEOP and control_state != "teleop":
                    terminate_process(PROCESS_NAMES.STUDENT_CODE)
                    name = test_name or "teleop"
                    spawn_process(PROCESS_NAMES.STUDENT_CODE, run_student_code, name, max_iter)
                    control_state = "teleop"
                    continue
                elif new_bad_thing.event == BAD_EVENTS.ENTER_AUTO and control_state != "auto":
                    terminate_process(PROCESS_NAMES.STUDENT_CODE)
                    spawn_process(PROCESS_NAMES.STUDENT_CODE, run_student_code, "autonomous")
                    control_state = "auto"
                    continue
                elif new_bad_thing.event == BAD_EVENTS.ENTER_IDLE and control_state != "idle":
                    control_state = "idle"
                    break
                print(new_bad_thing.event)
                non_test_mode_print(new_bad_thing.data)
                if new_bad_thing.event in restartEvents:
                    state_queue.put([SM_COMMANDS.SEND_CONSOLE, [new_bad_thing.getStudentError()]])
                    control_state = "idle"
                    if test_mode:
                        restart_count += 1
                    if not emergency_stopped and new_bad_thing.event is BAD_EVENTS.EMERGENCY_STOP:
                        emergency_stopped = True
                    break
            if test_mode:
                state_queue.put([SM_COMMANDS.RESET, []])
            terminate_process(PROCESS_NAMES.STUDENT_CODE)
            state_queue.put([SM_COMMANDS.SET_VAL, [
                runtime_pb2.RuntimeData.STUDENT_STOPPED, ["studentCodeState"], False]])
            state_queue.put([SM_COMMANDS.END_STUDENT_CODE, []])
            state_queue.put([HIBIKE_COMMANDS.DISABLE, []])
        non_test_mode_print(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
        print("Funtime Runtime is done having fun.")
        print("TERMINATING")
    except Exception as e:
        print(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
        print("Funtime Runtime had too much fun.")
        print(e)
        print("".join(traceback.format_tb(sys.exc_info()[2])))


def run_student_code(bad_things_queue, state_queue, pipe, test_name="", max_iter=None): # pylint: disable=too-many-locals
    try:
        import signal # pylint: disable=redefined-outer-name,reimported

        terminated = False

        def sig_term_handler(signum, frame): # pylint: disable=unused-argument
            nonlocal terminated
            terminated = True
        signal.signal(signal.SIGTERM, sig_term_handler)

        def timed_out_handler(signum, frame): # pylint: disable=unused-argument
            raise TimeoutError("studentCode timed out")
        signal.signal(signal.SIGALRM, timed_out_handler)

        def check_timed_out(func, *args):
            signal.alarm(RUNTIME_CONFIG.STUDENT_CODE_TIMELIMIT.value)
            func(*args)
            signal.alarm(0)

        signal.alarm(RUNTIME_CONFIG.STUDENT_CODE_TIMELIMIT.value)
        import studentCode
        signal.alarm(0)

        if test_name != "":
            test_name += "_"
        try:
            setup_fn = getattr(studentCode, test_name + "setup")
        except AttributeError:
            raise RuntimeError(
                "Student code failed to define '{}'".format(test_name + "setup"))
        try:
            main_fn = getattr(studentCode, test_name + "main")
        except AttributeError:
            raise RuntimeError(
                "Student code failed to define '{}'".format(test_name + "main"))

        ensure_is_function(test_name + "setup", setup_fn)
        ensure_is_function(test_name + "main", main_fn)
        ensure_not_overridden(studentCode, "Robot")

        studentCode.Robot = studentAPI.Robot(state_queue, pipe)
        studentCode.Gamepad = studentAPI.Gamepad(state_queue, pipe)
        studentCode.Actions = studentAPI.Actions
        studentCode.print = studentCode.Robot._print # pylint: disable=protected-access

        check_timed_out(setup_fn)

        exception_cell = [None]
        clarify_coroutine_warnings(exception_cell)

        async def main_loop():
            exec_count = 0
            while not terminated and (exception_cell[0] is None) and (
                    max_iter is None or exec_count < max_iter):
                next_call = loop.time() + 1. / RUNTIME_CONFIG.STUDENT_CODE_HZ.value
                studentCode.Robot._get_all_sensors() # pylint: disable=protected-access
                studentCode.Gamepad._get_gamepad() # pylint: disable=protected-access
                check_timed_out(main_fn)

                # Throttle sending print statements
                if (exec_count % 5) == 0:
                    studentCode.Robot._send_prints() # pylint: disable=protected-access

                sleep_time = max(next_call - loop.time(), 0.)
                state_queue.put([SM_COMMANDS.STUDENT_MAIN_OK, []])
                exec_count += 1
                await asyncio.sleep(sleep_time)
            if exception_cell[0] is not None:
                raise exception_cell[0] # pylint: disable=raising-bad-type
            if not terminated:
                bad_things_queue.put(
                    BadThing(
                        sys.exc_info(),
                        "Process Ended",
                        event=BAD_EVENTS.END_EVENT))

        loop = asyncio.get_event_loop()

        def my_exception_handler(loop, context): # pylint: disable=unused-argument
            if exception_cell[0] is None:
                exception_cell[0] = context["exception"]

        loop.set_exception_handler(my_exception_handler)
        loop.run_until_complete(main_loop())

    except TimeoutError:
        event = BAD_EVENTS.STUDENT_CODE_TIMEOUT
        bad_things_queue.put(BadThing(sys.exc_info(), event.value, event=event))
    except StudentAPIError:
        event = BAD_EVENTS.STUDENT_CODE_VALUE_ERROR
        bad_things_queue.put(BadThing(sys.exc_info(), event.value, event=event))
    except Exception as e:  # something broke in student code
        bad_things_queue.put(BadThing(sys.exc_info(), str(e), event=BAD_EVENTS.STUDENT_CODE_ERROR))


def start_state_manager(bad_things_queue, state_queue, runtime_pipe):
    try:
        state_manager = stateManager.StateManager(bad_things_queue, state_queue, runtime_pipe)
        state_manager.start()
    except Exception as e:
        bad_things_queue.put(BadThing(sys.exc_info(), str(e), event=BAD_EVENTS.STATE_MANAGER_CRASH))


def start_udp_sender(bad_things_queue, state_queue, sm_pipe):
    try:
        send_class = Ansible.UDPSendClass(bad_things_queue, state_queue, sm_pipe)
        send_class.start()
    except Exception as e:
        bad_things_queue.put(BadThing(sys.exc_info(), str(e), event=BAD_EVENTS.UDP_SEND_ERROR))


def start_udp_receiver(bad_things_queue, state_queue, sm_pipe):
    try:
        recv_class = Ansible.UDPRecvClass(bad_things_queue, state_queue, sm_pipe)
        recv_class.start()
    except Exception as e:
        bad_things_queue.put(BadThing(sys.exc_info(), str(e), event=BAD_EVENTS.UDP_RECV_ERROR))


def start_tcp(bad_things_queue, state_queue, sm_pipe):
    try:
        tcp_class = Ansible.TCPClass(bad_things_queue, state_queue, sm_pipe)
        tcp_class.start()
    except Exception as e:
        bad_things_queue.put(BadThing(sys.exc_info(), str(e), event=BAD_EVENTS.TCP_ERROR))


def process_factory(bad_things_queue, state_queue, stdout_redirect=None): # pylint: disable=unused-argument
    def spawn_process_helper(process_name, helper, *args):
        pipe_to_child, pipe_from_child = multiprocessing.Pipe()
        if process_name != PROCESS_NAMES.STATE_MANAGER:
            state_queue.put([SM_COMMANDS.ADD, [process_name, pipe_to_child]], block=True)
            pipe_from_child.recv()
        new_process = multiprocessing.Process(target=helper, name=process_name.value, args=[
            bad_things_queue, state_queue, pipe_from_child] + list(args))
        ALL_PROCESSES[process_name] = new_process
        new_process.daemon = True
        new_process.start()
    return spawn_process_helper


def terminate_process(process_name):
    if process_name not in ALL_PROCESSES:
        return
    process = ALL_PROCESSES.pop(process_name)
    process.terminate()
    for _ in range(100):  # Gives 1 sec for process to terminate
        time.sleep(.01)  # Give the OS a chance to terminate the other process
        if not process.is_alive():
            break
    if process.is_alive():
        print("Terminating with EXTREME PREJUDICE")
        print("Queue state is probably boned and we should restart entire runtime")
        print("Boned Process:", process_name)
        os.kill(process.pid, signal.SIGKILL)
        raise NotImplementedError


def runtime_test(test_names):
    # Normally dangerous. Allowed here because we put testing code there.
    import studentCode

    test_name_regex = re.compile(".*_setup")
    all_test_names = [test_name[:-len("_setup")]
                      for test_name in dir(studentCode) if test_name_regex.match(test_name)]

    if not test_names:
        print("Running all non-optional tests")
        test_names = [
            test_name for test_name in all_test_names if not test_name.startswith('optional')]
    else:
        for test_name in test_names:
            if test_name not in all_test_names:
                print("Error: {} not found.".format(test_name))
                return

    fail_count = 0
    failed_tests = []

    for test_name in test_names:
        if test_name in ["autonomous", "teleop"]:
            continue
        test_file_name = "%s_output" % (test_name,)
        with open(test_file_name, "w", buffering=1) as test_output:
            print("Running test: {}".format(test_name), end="", flush=True)
            sys.stdout = test_output

            ALL_PROCESSES.clear()

            runtime(test_name)

            # Terminate Ansible to free up ports for further tests
            terminate_process(PROCESS_NAMES.UDP_RECEIVE_PROCESS)
            if PROCESS_NAMES.UDP_SEND_PROCESS in ALL_PROCESSES:
                terminate_process(PROCESS_NAMES.UDP_SEND_PROCESS)
            if PROCESS_NAMES.TCP_PROCESS in ALL_PROCESSES:
                terminate_process(PROCESS_NAMES.TCP_PROCESS)
            sys.stdout = sys.__stdout__
            print("{}DONE!".format(" " * (50 - len(test_name))))

        if test_success(test_file_name):
            os.remove(test_file_name)
        else:
            # Explicitly set output to terminal, since we overwrote it earlier
            fail_count += 1
            failed_tests.append(test_name)

    # Restore output to terminal
    sys.stdout = sys.__stdout__
    if fail_count == 0:
        print("All {0} tests passed.".format(len(test_names)))
    else:
        print("{0} of the {1} tests failed.".format(fail_count, len(test_names)))
        print("Output saved in {{test_name}}_output.")
        print(
            "Inspect with 'diff {{test_name}}_output {0}{{test_name}}_output".format(
                RUNTIME_CONFIG.TEST_OUTPUT_DIR.value))
        for test_name in failed_tests:
            print("    {0}".format(test_name))
        sys.exit(1)


def test_success(test_file_name):
    expected_output = RUNTIME_CONFIG.TEST_OUTPUT_DIR.value + test_file_name
    test_output = test_file_name
    return filecmp.cmp(expected_output, test_output)


def start_hibike(bad_things_queue, state_queue, pipe):
    # bad_things_queue - queue to runtime
    # state_queue - queue to stateManager
    # pipe - pipe from statemanager
    def add_paths():
        """Modify sys.path so we can find hibike.
        """
        path = os.path.dirname(os.path.abspath(__file__))
        parent_path = path.rstrip("runtime")
        hibike = os.path.join(parent_path, "hibike")
        sys.path.insert(1, hibike)

    try:
        add_paths()
        import hibike_process # pylint: disable=import-error
        hibike_process.hibike_process(bad_things_queue, state_queue, pipe)
    except Exception as e:
        bad_things_queue.put(BadThing(sys.exc_info(), str(e)))


def ensure_is_function(tag, val):
    if inspect.iscoroutinefunction(val):
        raise RuntimeError("{} is defined with `async def` instead of `def`".format(tag))
    if not inspect.isfunction(val):
        raise RuntimeError("{} is not a function".format(tag))


def ensure_not_overridden(module, name):
    if hasattr(module, name):
        raise RuntimeError("Student code overrides `{}`, which is part of the API".format(name))


def clarify_coroutine_warnings(exception_cell):
    """
    Python's default error checking will print warnings of the form:
        RuntimeWarning: coroutine '???' was never awaited

    This function will will upgrade such a warning to a fatal error,
    while also injecting a additional clarification message about possible causes.
    """
    import warnings

    default_showwarning = warnings.showwarning

    def custom_showwarning(message, category, filename, lineno, file=None, line=None): # pylint: disable=too-many-arguments
        default_showwarning(message, category, filename, lineno, line)

        if str(message).endswith("was never awaited"):
            coro_name = str(message).split("'")[-2]

            print("""
The PiE API has upgraded the above RuntimeWarning to a runtime error!

This error typically occurs in one of the following cases:

1. Calling `Actions.sleep` or anything in `Actions` without using `await`.

Incorrect code:
    async def my_coro():
        Actions.sleep(1.0)

Consider instead:
    async def my_coro():
        await Actions.sleep(1.0)

2. Calling an `async def` function from inside `setup` or `loop` without using
`Robot.run`.

Incorrect code:
    def loop():
        my_coro()

Consider instead:
    def loop():
        Robot.run(my_coro)
""".format(coro_name=coro_name), file=file)
            exception_cell[0] = message

    warnings.showwarning = custom_showwarning


if __name__ == "__main__":
    parser = argparse.ArgumentParser() # pylint: disable=invalid-name
    parser.add_argument("-t", "--test", nargs="*",
                        help="Run specified tests. If no arguments, run all tests.")
    arguments = parser.parse_args() # pylint: disable=invalid-name
    if arguments.test is None:
        runtime()
    else:
        runtime_test(arguments.test)
