import unittest
import os
import time
from runtime.control import StudentCodeExecutor


class TestStudentCodeExecutor(unittest.TestCase):
    def get_abs_path(self, filename):
        return os.path.join(os.path.dirname(__file__), filename)

    def test_load_blank(self):
        StudentCodeExecutor(self.get_abs_path('studentcode/blank.py')).reload()

    def test_load_bad_syntax(self):
        with self.assertRaises(SyntaxError):
            StudentCodeExecutor(self.get_abs_path('studentcode/badsyntax.py')).reload()
