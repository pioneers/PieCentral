import os
from schema import And, Regex, Use


def get_module_path(filename: str) -> str:
    """ Return a path relative to the module's top-level directory. """
    module_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(module_dir, '..', filename)


VALID_NAME = Regex(r'^[a-zA-Z_]\w*$')
POSITIVE_INTEGER = And(int, lambda n: n > 0)
POSITIVE_REAL = And(Use(float), lambda x: x > 0)
