"""
runtime.executor
"""

import asyncio
import runtime.journal
from runtime.api import Actions, Gamepad, Robot
from runtime.devices import SensorService
from runtime.messaging import Circuitbreaker, make_rpc_server

LOGGER = runtime.journal.make_logger(__name__)


def blank_function():
    """ Blank function stub for replacing bad functions in student code. """


async def blank_coroutine():
    """ Blank coroutine function stub for replacing bad functions in student code. """


def default_coding_challenge(x: int) -> int:
    return None


class StudentCodeExecutor:
    required_functions = {
        'autonomous_setup': blank_function,
        'autonomous_main': blank_function,
        'teleop_setup': blank_function,
        'teleop_main': blank_function,
        'autonomous_actions': blank_coroutine,
    }

    coding_challenge = ('tennis_ball', 'remove_duplicates', 'rotate',
                        'next_fib', 'most_common', 'get_coins')

    def __init__(self, path: str):
        self.path = os.path.abspath(os.path.expanduser(path))
        dirname, basename = os.path.split(self.path)
        self.module_name, _ = os.path.splitext(basename)
        if dirname not in sys.path:
            sys.path.append(dirname)
            LOGGER.debug(f'Added "{dirname}" to "sys.path".')
        self.reload()

    def compose_challenge(self):
        functions = [getattr(self.module, challenge, default_coding_challenge)
                     for challenge in self.coding_challenge]
        return reduce(lambda f, g: (lambda x: g(f(x))), functions, lambda x: x)

    async def run_challenge(self, seed: int):
        challenge = self.compose_challenge()
        return challenge(seed)

    def patch(self, module):
        """ Monkey-patch student code. """
        module.Actions = Actions
        module.Robot = Robot
        module.Gamepad = Gamepad
        for name, default_function in self.required_functions.items():
            if not hasattr(module, name):
                setattr(module, name, default_function)

    def validate(self, module):
        for name, default_function in self.required_functions.items():
            function = getattr(module, name)
            if not inspect.isfunction(function):
                raise RuntimeExecutorException(f'"{name}" is not a function.',
                                               function_name=name)
            expects_coro = inspect.iscoroutinefunction(default_function)
            actually_coro = inspect.iscoroutinefunction(function)
            if expects_coro and not actually_coro:
                raise RuntimeExecutorException(
                    f'"{name}" is not a coroutine function when it should be.',
                    function_name=name,
                )
            if not expects_coro and actually_coro:
                raise RuntimeExecutorException(
                    f'"{name}" is a corountine function when it should not be.',
                    function_name=name,
                )
            if inspect.signature(default_function) != inspect.signature(function):
                raise RuntimeExecutorException(f'"{name}" signature is not correct.',
                                               function_name=name)

    def reload(self):
        if not hasattr(self, 'module'):
            self.module = importlib.import_module(self.module_name)
        else:
            self.module = importlib.reload(self.module)
        self.patch(self.module)
        self.validate(self.module)
        LOGGER.debug('Imported and patched student code module.')


class ExecutorService(SensorService):
    pass


async def start(options):
    server = await make_rpc_server(ExecutorService(options['dev_schema']), path=options['exec_srv'])
    async with server:
        await server.serve_forever()
