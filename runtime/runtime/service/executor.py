import asyncio
import collections
from concurrent.futures import ProcessPoolExecutor
import dataclasses
import enum
import functools
import importlib
import inspect
import os
import queue
import shutil
import signal
import tempfile
import threading
import time
import types
import typing
import uuid

import aiofiles
import pylint
import structlog
from schema import And, Optional, Regex, Schema, SchemaError, Use
import yaml

from runtime.game.studentapi import (
    Mode,
    Alliance,
    Actions,
    Match,
    Gamepad,
    Robot,
)
from runtime.service.base import Service
from runtime.util import (
    POSITIVE_INTEGER,
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
    LIST_DEVICE_NAMES = enum.auto()
    SET_DEVICE_NAME = enum.auto()
    DEL_DEVICE_NAME = enum.auto()


class ActionExecutor(threading.Thread):
    def __init__(self, name: str = 'action-executor'):
        self.running_actions = set()
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

    def register_action_threadsafe(self, action, *args):
        self.loop.call_soon_threadsafe(self.register_action, action, *args)

    def register_action(self, action: typing.Callable, *args):
        if not inspect.iscoroutinefunction(action):
            LOGGER.warn('Action should be a coroutine function')
        elif self.is_running(action):
            LOGGER.warn('Action is already running, ignoring', action=action.__name__)
        else:
            self.running_actions.add(action)
            action_task = asyncio.get_running_loop().create_task(action(*args))
            action_task.add_done_callback(functools.partial(self.unregister_action, action))
            LOGGER.debug('Registered action', action=action.__name__)

    def unregister_action(self, action: typing.Callable, *_):
        if action in self.running_actions:
            self.running_actions.remove(action)
            LOGGER.debug('Unregistered action', action=action.__name__)


class DeviceAliasManager(collections.UserDict):
    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        asyncio.create_task(self.load_initial_aliases())

    async def load_initial_aliases(self):
        try:
            async with aiofiles.open(self.filename) as alias_file:
                self.update(yaml.loads(await alias_file.read()))
        except FileNotFoundError:
            pass

    async def persist_aliases(self):
        tmp_path = os.path.join(tempfile.gettempdir(), f'dev-aliases-{uuid.uuid4()}')
        async with aiofiles.open(tmp_path, mode='w+') as alias_file:
            await alias_file.write(yaml.dump(self.data, default_flow_style=False))
        try:
            shutil.move(tmp_path, self.filename)
            LOGGER.debug('Persisted device aliases')
        finally:
            try:
                os.unlink(tmp_path)
                LOGGER.error('Failed to move temporary device aliases file')
            except OSError:
                pass

    def __setitem__(self, uid: typing.Union[str, int], alias: str):
        super().__setitem__(str(uid), alias)
        asyncio.create_task(self.persist_aliases())

    def __delitem__(self, uid: typing.Union[str, int]):
        super().__delitem__(str(uid))
        asyncio.create_task(self.persist_aliases())


def handle_timeout(_signum, _stack_frame):
    raise TimeoutError('Task timed out')


def run_with_timeout(fn: typing.Callable[[], typing.Any], timeout: float, *args, **kwargs):
    signal.setitimer(signal.ITIMER_REAL, timeout)
    try:
        return fn(*args, **kwargs)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def _print(*values, sep=' ', _file=None, _flush=False):
    LOGGER.info(sep.join(map(str, values)))


CHALLENGE_FN = typing.Callable[[int], int]


def run_challenge(challenges: typing.Iterable[CHALLENGE_FN], seed: int) -> int:
    try:
        reducer = lambda result, challenge: challenge(result)
        return functools.reduce(reducer, challenges, seed)
    except Exception as exc:
        LOGGER.error('Failed to run challenge', exc=str(exc))


@dataclasses.dataclass
class Executor:
    match: Match
    config: typing.Any
    mode_queue: queue.Queue
    student_code: types.ModuleType = None
    action_executor: ActionExecutor = dataclasses.field(default_factory=ActionExecutor)

    def get_functions(self, mode: Mode):
        if mode is Mode.AUTO:
            prefix = 'autonomous'
        elif mode is Mode.TELEOP:
            prefix = 'teleop'
        else:
            raise RuntimeBaseException('Cannot execute mode', mode=mode.name)
        return (
            getattr(self.student_code, f'{prefix}_setup'),
            getattr(self.student_code, f'{prefix}_main'),
        )

    def import_student_code(self):
        if not self.student_code:
            self.student_code = importlib.import_module(self.config['student_code'])
        else:
            self.student_code = importlib.reload(self.student_code)

    def reload_student_code(self):
        run_with_timeout(self.import_student_code, self.config['import_timeout'])
        self.student_code.print = _print
        self.student_code.Actions = Actions
        self.student_code.Alliance = Alliance
        self.student_code.Mode = Mode
        self.student_code.Match = self.match
        self.student_code.Robot = Robot()
        self.student_code.Robot.run = self.action_executor.register_action_threadsafe
        self.student_code.Robot.is_running = self.action_executor.is_running

    # def run_challenge(self, challenges: typing.Iterable[CHALLENGE_FN], seed: int) -> int:
    #     if not self.student_code:
    #         self.reload_student_code()
    #     result = seed
    #     for challenge_name in challenges:
    #         challenge = getattr(self.student_code, challenge_name)
    #         result = challenge(result)
    #     return result

    def run_cycle(self, main, loop_interval):
        try:
            main()
        except Exception as exc:
            LOGGER.error('Unable to run main', fn=main.__name__, exc=str(exc))
            if isinstance(exc, TimeoutError):
                raise
        finally:
            time.sleep(loop_interval)

    def loop(self, mode: Mode):
        setup, main = self.get_functions(mode)
        try:
            run_with_timeout(setup, self.config['setup_timeout'])
        except Exception as exc:
            LOGGER.error('Unable to run setup', fn=setup.__name__, exc=str(exc))
        loop_interval = self.config['loop_interval']
        signal.setitimer(signal.ITIMER_REAL, loop_interval, loop_interval)
        while self.mode_queue.empty():
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
            mode = self.mode_queue.get()
            LOGGER.debug('Changing mode', mode=mode.name)
            if mode is Mode.ESTOP:
                raise EmergencyStopException
            elif mode is not Mode.IDLE:
                try:
                    self.reload_student_code()
                except Exception as exc:
                    LOGGER.error('Unable to import student code', exc=str(exc))
                else:
                    self.loop(mode)


@dataclasses.dataclass
class ExecutorService(Service):
    access: asyncio.Lock = dataclasses.field(default_factory=asyncio.Lock)
    match: Match = dataclasses.field(default_factory=Match)
    mode_queue: queue.Queue = dataclasses.field(default_factory=queue.Queue)
    executor: Executor = dataclasses.field(init=False, default=None)

    config_schema = dict(Service.config_schema)
    config_schema.update({
        'student_code': str,
        'device_aliases': Use(get_module_path),
        Optional('loop_interval', default=0.03): POSITIVE_REAL,
        Optional('import_timeout', default=2): POSITIVE_REAL,
        Optional('setup_timeout', default=1): POSITIVE_REAL,
        Optional('challenge_timeout', default=5): POSITIVE_REAL,
    })

    request_schema = Schema({
        'type': And(Use(str.upper), Use(RequestType.__getitem__)),
        Optional('mode'): And(Use(str.upper), Use(Mode.__getitem__)),
        Optional('alliance'): And(Use(str.upper), Use(Alliance.__getitem__)),
        Optional('challenges', default=[]): [VALID_NAME],
        Optional('seed'): int,
        Optional('name_assignment'): {
            'name': VALID_NAME,
            Optional('uid'): Use(int),
        }
    })

    def __post_init__(self):
        self.executor = Executor(self.match, self.config, self.mode_queue)

    async def get_match(self):
        async with self.access:
            return self.match.as_dict()

    async def set_match(self, request: dict):
        """ Set the match information. """
        async with self.access:
            self.match.alliance, self.match.mode = request['alliance'], request['mode']
            self.mode_queue.put_nowait(self.match.mode)
            return self.match.as_dict()

    async def run_challenge(self, request: dict):
        self.executor.reload_student_code()
        challenges = [getattr(self.executor.student_code, challenge)
                      for challenge in request['challenges']]
        with ProcessPoolExecutor() as executor:
            loop = asyncio.get_running_loop()
            answer = await loop.run_in_executor(executor, run_challenge,
                                                challenges, request['seed'])
            return {'answer': answer}

    async def dispatch_command(self, request: dict, aliases: DeviceAliasManager):
        commands = {
            RequestType.GET_MATCH: self.get_match,
            RequestType.SET_MATCH: lambda: self.set_match(request),
            RequestType.RUN_CHALLENGE: lambda: self.run_challenge(request),
        }
        return await commands[request['type']]()

    async def main(self):
        aliases = DeviceAliasManager(self.config['device_aliases'])
        command_conn = self.connections['command']
        while True:
            request, response = await command_conn.recv(), {'received': time.time()}
            LOGGER.debug('Received request', **request)
            try:
                request = self.request_schema.validate(request) or {}
                response.update(await self.dispatch_command(request, aliases) or {})
            except SchemaError as exc:
                response['exc'] = str(exc)
                LOGGER.error('Received bad command, treating as no-op', **response)
            except RuntimeBaseException as exc:
                response['exc'] = str(exc)
                response.update(exc.context)
                LOGGER.error('Unable to execute command', **response)
            finally:
                response['completed'] = time.time()
                await command_conn.send(response)
                response.clear()

    def __call__(self):
        # A necessary hack to ensure SIGALARM is delivered to the thread
        # running student code on timeouts. (Signal handlers run in the main
        # thread, i.e., the thread the interpreter was started in.)
        server_thread = threading.Thread(target=lambda: asyncio.run(self.bootstrap()),
                                         daemon=True, name='command-server')
        server_thread.start()
        signal.signal(signal.SIGALRM, handle_timeout)
        self.executor.spin()
