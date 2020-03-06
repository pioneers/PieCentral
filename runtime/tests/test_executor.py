import multiprocessing
import signal
import time
import threading

import pytest

from runtime.service.executor import (
    ExecutorService,
    StudentCodeExecutor,
    handle_timeout,
    run_with_timeout,
)
from runtime.game.studentapi import Match


# @pytest.fixture
# def student_code_executor():
#     return StudentCodeExecutor({
#         'import_timeout': 0.1,
#     }, Match(), threading.Event(), {}, {})
#
#
# def test_run_with_timeout():
#     def slow():
#         time.sleep(0.15)
#
#     def target(timed_out):
#         signal.signal(signal.SIGALRM, handle_timeout)
#         try:
#             run_with_timeout(slow, 0.1)
#         except TimeoutError:
#             timed_out.set()
#
#     timed_out = multiprocessing.Event()
#     child = multiprocessing.Process(target=target, args=(timed_out, ))
#     child.start()
#     child.join()
#     assert timed_out.is_set()
#
#
# @pytest.mark.parametrize('bad_module', [
#     'studentcode.badimport.badsyntax',
#     'studentcode.badimport.infloop',
#     'studentcode.badimport.noattr',
#     'studentcode.badimport.recursion',
#     'studentcode.badimport.zerodiv',
# ])
# def test_bad_code(student_code_executor, bad_module):
#     def target(import_failed):
#         signal.signal(signal.SIGALRM, handle_timeout)
#         student_code_executor.reload_student_code(bad_module)
#         if not student_code_executor.last_import_succeeded:
#             import_failed.set()
#
#     import_failed = multiprocessing.Event()
#     child = multiprocessing.Process(target=target, args=(import_failed, ))
#     child.start()
#     child.join()
#     assert import_failed.is_set()
#
#
# def test_empty_code():
#     pass
#
#
# def test_bad_code_replacement():
#     pass
