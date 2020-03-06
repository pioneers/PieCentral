import asyncio
import inspect
import multiprocessing
import signal
import time
import threading

import pytest

from runtime.service.executor import (
    ActionExecutor,
    ExecutorService,
    StudentCodeExecutor,
    handle_timeout,
    run_challenge,
    run_with_timeout,
)
from runtime.game.studentapi import Match, Mode
from runtime.util.exception import RuntimeBaseException


@pytest.fixture
async def action_executor():
    action_executor = ActionExecutor()
    action_executor.start()
    await asyncio.sleep(0.1)
    yield action_executor
    action_executor.loop.stop()


@pytest.fixture
def executor():
    executor = StudentCodeExecutor({
        'import_timeout': 0.1,
    }, Match(), threading.Event(), {}, {})
    with executor:
        yield executor


@pytest.mark.timeout(5)
def test_action_executor_single(action_executor):
    ran = threading.Event()
    async def action(arg):
        if arg:
            ran.set()
    action_executor.register_action_threadsafe(action, True)
    ran.wait()


@pytest.mark.asyncio
async def test_action_executor_multiple(action_executor):
    async def infinite_loop1():
        while True:
            await asyncio.sleep(1)

    async def infinite_loop2():
        while True:
            await asyncio.sleep(1)

    for _ in range(10):
        action_executor.register_action_threadsafe(infinite_loop1)
        action_executor.register_action_threadsafe(infinite_loop2)

    await asyncio.sleep(0.1)
    assert action_executor.is_running(infinite_loop1)
    assert action_executor.is_running(infinite_loop2)
    assert len(action_executor.running_actions) == 2
    action_executor.unregister_all()
    await asyncio.sleep(0.1)
    assert len(action_executor.running_actions) == 0


@pytest.mark.asyncio
async def test_action_executor_bad(action_executor):
    def action():
        pass

    action_executor.register_action_threadsafe(action)
    await asyncio.sleep(0.1)
    assert not action_executor.is_running(action)


# def test_run_with_timeout():
#     def slow():
#         time.sleep(0.2)
#
#     def target():
#         signal.signal(signal.SIGALRM, handle_timeout)
#         run_with_timeout(slow, 0.1)
#
#     child = multiprocessing.Process(target=target)
#     child.start()
#     child.join()
#     assert child.exitcode != 0


@pytest.mark.parametrize('bad_module', [
    'studentcode.badimport.badsyntax',
    'studentcode.badimport.infloop',
    'studentcode.badimport.noattr',
    'studentcode.badimport.recursion',
    'studentcode.badimport.zerodiv',
])
def test_bad_code(executor, bad_module):
    def target():
        signal.signal(signal.SIGALRM, handle_timeout)
        executor.reload_student_code(bad_module)
        assert not executor.last_import_succeeded

    child = multiprocessing.Process(target=target)
    child.start()
    child.join()
    assert child.exitcode == 0


# def test_reload(executor):
#     executor.import_student_code('studentcode.blank')
#     assert not hasattr(executor.student_code, 'teleop_setup')
#     print(executor.student_code)
#     executor.student_code.teleop_setup = lambda: True
#     executor.import_student_code('studentcode.blank')
#     assert executor.student_code.teleop_setup() is True


@pytest.mark.parametrize('module', [
    'studentcode.blank',
    'studentcode.correct',
])
def test_empty_code(executor, module):
    executor.import_student_code(module)
    assert executor.last_import_succeeded
    for mode in [Mode.AUTO, Mode.TELEOP]:
        executor.match.mode = mode
        setup, main = executor.get_functions()
        assert inspect.isfunction(setup) and not inspect.iscoroutinefunction(setup)
        assert inspect.isfunction(main) and not inspect.iscoroutinefunction(main)
        assert setup() is None
        assert main() is None


def test_get_functions_idle_modes(executor):
    for mode in [Mode.IDLE, Mode.ESTOP]:
        executor.match.mode = mode
        with pytest.raises(RuntimeBaseException):
            executor.get_functions()


def test_run_challenge():
    def double(x):
        return 2 * x
    def incr(x):
        return x + 1
    def faulty(x):
        raise ValueError
    assert run_challenge([double, incr], 3) == [3, 6, 7]
    assert run_challenge([], 9) == [9]
    assert run_challenge(9, 9) is None
    assert run_challenge([double, faulty], 3) is None


# def test_bad_code_replacement():
#     pass
