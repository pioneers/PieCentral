import asyncio
from concurrent.futures import ProcessPoolExecutor
import dataclasses
import enum
import functools
import importlib
import inspect
from numbers import Real
import signal
import threading
import time
import types
import typing

from pylint import epylint as lint
import structlog
from schema import Optional, Use

from runtime.game.studentapi import (
    DeviceAliasManager,
    Mode,
    Alliance,
    Action,
    Actions,
    Match,
    Gamepad,
    Robot,
)
from runtime.messaging.device import DeviceMapping, get_device_type
from runtime.service.base import Service
from runtime.util import (
    POSITIVE_REAL,
    VALID_NAME,
    get_module_path,
)
from runtime.util.exception import EmergencyStopException, RuntimeBaseException


LOGGER = structlog.get_logger()


class RequestType(enum.Enum):
    GET_MATCH = enum.auto()
    SET_MATCH = enum.auto()
    RUN_CHALLENGE = enum.auto()
    LIST_ALIASES = enum.auto()
    SET_ALIAS = enum.auto()
    DEL_ALIAS = enum.auto()
    LINT = enum.auto()


class ActionExecutor(threading.Thread):
    def __init__(self, name: str = 'action-executor'):
        self.running_actions, self.loop = dict(), None
        super().__init__(target=self, daemon=True, name=name)

    def __call__(self):
        # Need to explicitly create a new loop instead of using `get_event_loop`,
        # since this is not the main thread (https://stackoverflow.com/a/55278365).
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    def is_running(self, action):
        return action in self.running_actions

    def register_action_threadsafe(self, action, *args, timeout: Real = 30):
        self.loop.call_soon_threadsafe(self.register_action, action, timeout, *args)

    def unregister_all(self):
        for action in self.running_actions:
            self.loop.call_soon_threadsafe(self.unregister_action, action)

    def register_action(self, action: Action, timeout: Real, *args):
        if not inspect.iscoroutinefunction(action):
            LOGGER.warn('Action should be a coroutine function')
        elif self.is_running(action):
            LOGGER.warn('Action is already running, ignoring', action=action.__name__)
        else:
            loop = asyncio.get_running_loop()
            timed_action = asyncio.wait_for(action(*args), timeout)
            self.running_actions[action] = action_task = loop.create_task(timed_action)
            action_task.add_done_callback(functools.partial(self.unregister_action, action))
            LOGGER.debug('Registered action', action=action.__name__)

    def unregister_action(self, action: Action, *_):
        try:
            self.running_actions.pop(action).cancel()
            LOGGER.debug('Unregistered action', action=action.__name__)
        except KeyError:
            LOGGER.debug('Attempted to unregister action not running', action=action.__name__)


def handle_timeout(_signum: int, _stack_frame):
    raise TimeoutError('Task timed out')


def run_with_timeout(func: typing.Callable[[], typing.Any], timeout: Real, *args, **kwargs):
    signal.setitimer(signal.ITIMER_REAL, float(timeout))
    try:
        return func(*args, **kwargs)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


Challenge = typing.Callable[[int], int]


def run_challenge(challenges: typing.Iterable[Challenge], seed: int) -> int:
    try:
        reducer = lambda result, challenge: challenge(result)
        return functools.reduce(reducer, challenges, seed)
    except Exception as exc:
        LOGGER.error('Failed to run challenge', exc=str(exc))


@dataclasses.dataclass
class StudentCodeExecutor:
    config: dict
    match: Match
    mode_changed: threading.Event
    device_buffers: DeviceMapping
    aliases: DeviceAliasManager
    action_executor: ActionExecutor = dataclasses.field(default_factory=ActionExecutor)
    student_code: types.ModuleType = dataclasses.field(init=False, default=None)

    def __enter__(self):
        return self

    def __exit__(self, _type, _exc, _traceback):
        self.device_buffers.clear()

    def get_function(self, name: str):
        try:
            func = getattr(self.student_code, name)
        except AttributeError:
            LOGGER.warn('Unable to get function, using stub', func=name)
            func = lambda: None
        return func

    def get_functions(self):
        if self.match.mode is Mode.AUTO:
            prefix = 'autonomous'
        elif self.match.mode is Mode.TELEOP:
            prefix = 'teleop'
        else:
            raise RuntimeBaseException('Cannot execute mode', mode=self.match.mode.name)
        return (self.get_function(f'{prefix}_setup'), self.get_function(f'{prefix}_main'))

    @property
    def last_import_succeeded(self):
        return hasattr(self.student_code, '__file__')

    def import_student_code(self, student_code_name: str):
        if not self.student_code or not self.last_import_succeeded:
            self.student_code = importlib.import_module(student_code_name)
        else:
            self.student_code = importlib.reload(self.student_code)

    def reload_student_code(self, student_code_name: str):
        import_task = functools.partial(self.import_student_code, student_code_name)
        try:
            run_with_timeout(import_task, self.config['import_timeout'])
        except Exception as exc:
            self.student_code = types.ModuleType(student_code_name)
            LOGGER.warn('Unable to import student code', exc=str(exc))

        logger = structlog.get_logger(student_code_name)
        def _print(*values, sep=' ', _file=None, _flush=False):
            logger.info(sep.join(map(str, values)))

        self.student_code.print = _print
        self.student_code.Actions = Actions
        self.student_code.Alliance = Alliance
        self.student_code.Mode = Mode
        self.student_code.Match = self.match
        self.student_code.Robot = Robot(self.device_buffers, self.action_executor, self.aliases)
        self.student_code.Gamepad = Gamepad(self.device_buffers, self.match.mode)

    def run_cycle(self, main, loop_interval):
        try:
            main()
        except Exception as exc:
            LOGGER.error('Unable to run main', func=main.__name__, exc=str(exc))
            if isinstance(exc, TimeoutError):
                raise
        finally:
            time.sleep(loop_interval)

    def loop(self):
        setup, main = self.get_functions()
        try:
            run_with_timeout(setup, self.config['setup_timeout'])
        except Exception as exc:
            LOGGER.error('Unable to run setup', func=setup.__name__, exc=str(exc))
        loop_interval = self.config['loop_interval']
        signal.setitimer(signal.ITIMER_REAL, loop_interval, loop_interval)
        while not self.mode_changed.is_set():
            try:
                self.run_cycle(main, loop_interval)
            except TimeoutError:
                pass
            else:
                LOGGER.warn('Timer never ticked')
        signal.setitimer(signal.ITIMER_REAL, 0)

    def spin(self):
        self.action_executor.start()
        while True:
            self.mode_changed.wait()
            self.mode_changed.clear()
            LOGGER.debug('Setting match information', mode=self.match.mode.name,
                         alliance=self.match.mode.name)
            if self.match.mode is Mode.ESTOP:
                raise EmergencyStopException
            self.action_executor.unregister_all()
            if self.match.mode is not Mode.IDLE:
                self.reload_student_code(self.config['student_code'])
                self.loop()


@dataclasses.dataclass
class ExecutorService(Service):
    access: asyncio.Lock = dataclasses.field(default_factory=asyncio.Lock)
    match: Match = dataclasses.field(default_factory=Match)
    mode_changed: threading.Event = dataclasses.field(default_factory=threading.Event)
    devices_buffers: DeviceMapping = dataclasses.field(init=False, default=None)
    aliases: DeviceAliasManager = dataclasses.field(init=False, default=None)
    executor: StudentCodeExecutor = dataclasses.field(init=False, default=None)

    request, response = 0, 1

    config_schema = {
        **Service.config_schema,
        'student_code': str,
        'device_aliases': Use(get_module_path),
        Optional('loop_interval', default=0.03): POSITIVE_REAL,
        Optional('import_timeout', default=2): POSITIVE_REAL,
        Optional('setup_timeout', default=1): POSITIVE_REAL,
        Optional('challenge_timeout', default=5): POSITIVE_REAL,
        Optional('persist_timeout', default=5): POSITIVE_REAL,
        Optional('device_timeout', default=1): POSITIVE_REAL,
    }

    def __post_init__(self):
        self.device_buffers = DeviceMapping(self.config['device_timeout'], LOGGER)

    async def bootstrap(self):
        self.aliases = DeviceAliasManager(self.config['device_aliases'],
                                          self.config['persist_timeout'], LOGGER)
        self.executor = StudentCodeExecutor(self.config, self.match, self.mode_changed,
                                            self.device_buffers, self.aliases)
        asyncio.create_task(self.aliases.load_initial_aliases())
        await super().bootstrap()

    async def get_match(self):
        async with self.access:
            return self.match.as_dict()

    async def set_match(self, mode: str, alliance: str):
        """ Set the match information. """
        async with self.access:
            self.match.mode = Mode.__members__[mode.upper()]
            self.match.alliance = Alliance.__members__[alliance.upper()]
            self.mode_changed.set()
            return self.match.as_dict()

    async def run_challenge(self, challenges: typing.List[str], seed: int):
        challenges = [getattr(self.executor.student_code, challenge)
                      for challenge in challenges]
        with ProcessPoolExecutor() as executor:
            loop = asyncio.get_running_loop()
            answer = await loop.run_in_executor(executor, run_challenge, challenges, seed)
            LOGGER.info('Completed coding challenge', seed=seed, answer=answer,
                        challenges=challenges)
            # Serialize as a string, since the answer may exceed the capacity of an unsigned long.
            return {'answer': str(answer)}

    async def list_aliases(self):
        async with self.access:
            return {'aliases': dict(self.aliases.data)}

    async def set_alias(self, name: str, uid: str):
        async with self.access:
            self.aliases[name] = uid
            return {'aliases': dict(self.aliases.data)}

    async def del_alias(self, name: str):
        async with self.access:
            try:
                del self.aliases[name]
            except KeyError as exc:
                raise RuntimeBaseException('No such alias', name=name) from exc
            return {'aliases': dict(self.aliases.data)}

    async def lint(self):
        student_code = self.executor.student_code
        if hasattr(student_code, '__file__'):
            # TODO: ignore some lint issues
            stdout, stderr = lint.py_run(student_code.__file__, return_std=True)
            return {'stdout': stdout.read(), 'stderr': stderr.read()}
        raise RuntimeBaseException('Unable to lint student code (failed to import)')

    async def listen_for_device_status(self):
        while True:
            status = await self.connections.device_status.recv()
            devices = status.get('devices') or []
            for device in devices:
                device_type = get_device_type(device_name=device['device_type'])
                await self.device_buffers.open(device['device_uid'], device_type)

    async def recv_request(self, command_conn):
        message_type, message_id, method, params = await command_conn.recv()
        context = {'message_id': message_id, 'method': method}
        if message_type != self.request:
            raise RuntimeBaseException('Received malformed request', **context)
        if method.upper() not in RequestType.__members__:
            raise RuntimeBaseException('Method not found', **context)
        LOGGER.debug('Received request', **context)
        return message_id, functools.partial(getattr(self, method), *params)

    async def send_response(self, command_conn, response):
        try:
            await command_conn.send(response)
        except OverflowError:
            response[3] = None
            LOGGER.error('Encountered overflow error')
            await command_conn.send(response)
        finally:
            LOGGER.debug('Sent response', message_id=response[1])

    async def main(self):
        asyncio.create_task(self.listen_for_device_status())
        while True:
            result = {'received': time.time()}
            response = [self.response, None, None, result]
            try:
                response[1], method = await self.recv_request(self.connections.command)
                result.update((await method()) or {})
            except Exception as exc:
                response[2], context = str(exc), getattr(exc, 'context', {})
                LOGGER.error('Unable to execute command', **context, error=response[2])
            finally:
                result['completed'] = time.time()
                await self.send_response(self.connections.command, response)

    def __call__(self):
        threading.current_thread().name = type(self).__name__.lower()
        signal.signal(signal.SIGALRM, handle_timeout)
        command_thread = threading.Thread(target=lambda: asyncio.run(self.bootstrap()),
                                          daemon=True, name='command-thread')
        command_thread.start()
        self.executor.reload_student_code(self.config['student_code'])
        with self.executor:
            self.executor.spin()
