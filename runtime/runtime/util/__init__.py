import os
from typing import Callable, Mapping, Sequence


def get_module_path(filename: str) -> str:
    """ Return a path relative to the module's top-level directory. """
    module_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(module_dir, '..', filename)


def accept_decorators(cls):
    """
    Decorate a class to accept decorators at object instantiation time.
    """
    class Proxy(cls):
        def __init__(self, *args, decorators: Mapping[str, Sequence[Callable]] = None, **kwargs):
            super().__init__(*args, **kwargs)
            decorators = decorators or {}
            for name, decorators in decorators.items():
                method = getattr(self, name)
                setattr(self, method, decorator(method))
    Proxy.__name__ = cls.__name__
    Proxy.__doc__ = cls.__doc__
    return Proxy
