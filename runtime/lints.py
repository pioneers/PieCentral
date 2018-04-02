import astroid

from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker

def register(linter):
    linter.register_checker(ImportStudentCode(linter))

class ImportStudentCode(BaseChecker):
    """
    An extra lint to ensure that studentCode isn't imported anywhere but
    the appropriate places.
    """
    __implements__ = IAstroidChecker


    OK_TO_IMPORT_FUNCTIONS = {'run_student_code', 'runtime_test'}

    name = 'import-student-code'
    priority = -1
    msgs = {
        'E9999': (
            'Imports studentCode',
            'no-import-student-code',
            "You shouldn't import student code, except in run_student_code"
        ),
    }

    def __init__(self, linter=None):
        super(ImportStudentCode, self).__init__(linter)
        self._stack = []

    def _ok_to_import(self):
        """Are we inside a function where it's ok to import studentCode?"""
        return len(self._stack) > 0 and len(self.OK_TO_IMPORT_FUNCTIONS & set(self._stack)) > 0

    def visit_functiondef(self, node):
        self._stack.append(node.name)

    def leave_functiondef(self, node):
        self._stack.pop()

    def visit_importfrom(self, node):
        if node.modname == 'studentCode':
            if not self._ok_to_import():
                self.add_message('no-import-student-code', node=node)

    def visit_import(self, node):
        mods = [name[0] for name in node.names]
        if 'studentCode' in mods:
            if not self._ok_to_import():
                self.add_message('no-import-student-code', node=node)
