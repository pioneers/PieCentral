import asyncio
import collections
from concurrent.futures import ProcessPoolExecutor
import dataclasses
import enum
import functools
import importlib
import inspect
import multiprocessing
from multiprocessing.connection import Connection as ProcessConnection
from numbers import Real
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
    LIST_ALIASES = enum.auto()
    SET_ALIAS = enum.auto()
    DEL_ALIAS = enum.auto()
    LINT = enum.auto()


class ActionExecutor(threading.Thread):
    def __init__(self, name: str = 'action-executor'):
        self.running_actions = dict()
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

    def unregister_all(self):
        for action in self.running_actions:
            self.loop.call_soon_threadsafe(self.unregister_action, action)

    def register_action(self, action: typing.Callable, *args):
        if not inspect.iscoroutinefunction(action):
            LOGGER.warn('Action should be a coroutine function')
        elif self.is_running(action):
            LOGGER.warn('Action is already running, ignoring', action=action.__name__)
        else:
            loop = asyncio.get_running_loop()
            self.running_actions[action] = action_task = loop.create_task(action(*args))
            action_task.add_done_callback(functools.partial(self.unregister_action, action))
            LOGGER.debug('Registered action', action=action.__name__)

    def unregister_action(self, action: typing.Callable, *_):
        try:
            self.running_actions.pop(action).cancel()
            LOGGER.debug('Unregistered action', action=action.__name__)
        except KeyError:
            LOGGER.debug('Attempted to unregister action not running', action=action.__name__)


class DeviceAliasManager(collections.UserDict):
    def __init__(self, filename: str, persist_timeout: Real):
        super().__init__()
        self.filename, self.persist_timeout = filename, persist_timeout
        self.persisting = asyncio.Lock()
        asyncio.create_task(asyncio.wait_for(self.load_initial_aliases(), self.persist_timeout))

    async def load_initial_aliases(self):
        async with self.persisting:
            try:
                async with aiofiles.open(self.filename) as alias_file:
                    self.data.update(yaml.load(await alias_file.read()))
                LOGGER.debug('Loaded initial aliases', aliases=self.data)
            except FileNotFoundError:
                pass

    async def persist_aliases(self):
        async with self.persisting:
            tmp_path = os.path.join(tempfile.gettempdir(), f'dev-aliases-{uuid.uuid4()}')
            async with aiofiles.open(tmp_path, mode='w+') as alias_file:
                await alias_file.write(yaml.dump(self.data, default_flow_style=False))
            try:
                shutil.move(tmp_path, self.filename)
                LOGGER.debug('Persisted device aliases', aliases=self.data)
            finally:
                try:
                    os.unlink(tmp_path)
                    LOGGER.error('Failed to move temporary device aliases file')
                except OSError:
                    pass

    def __setitem__(self, name: str, uid: typing.Union[str, int]):
        super().__setitem__(name, uid)
        asyncio.create_task(asyncio.wait_for(self.persist_aliases(), self.persist_timeout))

    def __delitem__(self, name: str):
        super().__delitem__(name)
        asyncio.create_task(asyncio.wait_for(self.persist_aliases(), self.persist_timeout))


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


Challenge = typing.Callable[[int], int]
Pipe = typing.Tuple[ProcessConnection, ProcessConnection]


def run_challenge(challenges: typing.Iterable[Challenge], seed: int) -> int:
    try:
        reducer = lambda result, challenge: challenge(result)
        return functools.reduce(reducer, challenges, seed)
    except Exception as exc:
        LOGGER.error('Failed to run challenge', exc=str(exc))


class StudentCodeExecutor(multiprocessing.Process):
    # TODO: handle unlimited recursion
    def __init__(self, config, match_receiver: ProcessConnection):
        self.config, self.match_receiver = config, match_receiver
        self.student_code, self.action_executor = None, ActionExecutor()
        super().__init__(name='student-code-executor', daemon=True, target=self.spin)

    def run(self):
        signal.signal(signal.SIGALRM, handle_timeout)
        self.action_executor.start()
        super().run()

    def get_function(self, name: str):
        try:
            fn = getattr(self.student_code, name)
        except AttributeError:
            LOGGER.warn('Unable to get function, using stub', fn=name)
            fn = lambda: None
        return fn

    def get_functions(self, mode: Mode):
        if mode is Mode.AUTO:
            prefix = 'autonomous'
        elif mode is Mode.TELEOP:
            prefix = 'teleop'
        else:
            raise RuntimeBaseException('Cannot execute mode', mode=mode.name)
        return (self.get_function(self.student_code, f'{prefix}_setup'),
                self.get_function(self.student_code, f'{prefix}_main'))

    def import_student_code(self):
        if not self.student_code:
            self.student_code = importlib.import_module(self.config['student_code'])
        else:
            self.student_code = importlib.reload(self.student_code)

    def reload_student_code(self, match):
        run_with_timeout(self.import_student_code, self.config['import_timeout'])
        self.student_code.print = _print
        self.student_code.Actions = Actions
        self.student_code.Alliance = Alliance
        self.student_code.Mode = Mode
        self.student_code.Match = match
        self.student_code.Robot = Robot(self.action_executor)
        self.student_code.Gamepad = Gamepad(match.mode)

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
        while not self.match_receiver.poll():
            try:
                self.run_cycle(main, loop_interval)
            except TimeoutError:
                pass
            else:
                LOGGER.warn('Timer never ticked')
        signal.setitimer(signal.ITIMER_REAL, 0)

    def spin(self):
        while True:
            match = self.match_receiver.recv()
            LOGGER.debug('Setting match information', mode=match.mode.name,
                         alliance=match.mode.name)
            if match.mode is Mode.ESTOP:
                raise EmergencyStopException
            self.action_executor.unregister_all()
            if match.mode is not Mode.IDLE:
                try:
                    self.reload_student_code(match)
                except Exception as exc:
                    LOGGER.error('Unable to import student code', exc=str(exc))
                else:
                    self.loop(match.mode)


@dataclasses.dataclass
class ExecutorService(Service):
    access: asyncio.Lock = dataclasses.field(default_factory=asyncio.Lock)
    match: Match = dataclasses.field(default_factory=Match)
    match_pipe: Pipe = dataclasses.field(default_factory=lambda: multiprocessing.Pipe(False))
    aliases: DeviceAliasManager = dataclasses.field(init=False, default=None)
    executor: StudentCodeExecutor = dataclasses.field(init=False, default=None)

    config_schema = {
        **Service.config_schema,
        'student_code': str,
        'device_aliases': Use(get_module_path),
        Optional('loop_interval', default=0.03): POSITIVE_REAL,
        Optional('import_timeout', default=2): POSITIVE_REAL,
        Optional('setup_timeout', default=1): POSITIVE_REAL,
        Optional('challenge_timeout', default=5): POSITIVE_REAL,
        Optional('persist_timeout', default=5): POSITIVE_REAL,
    }

    request_schema = Schema({
        'type': And(Use(str.upper), Use(RequestType.__getitem__)),
        Optional('mode'): And(Use(str.upper), Use(Mode.__getitem__)),
        Optional('alliance'): And(Use(str.upper), Use(Alliance.__getitem__)),
        Optional('challenges', default=[]): [VALID_NAME],
        Optional('seed'): int,
        Optional('alias'): {
            'name': VALID_NAME,
            Optional('uid'): Use(int),
        }
    })

    def __post_init__(self):
        self.aliases = DeviceAliasManager(self.config['device_aliases'],
                                          self.config['persist_timeout'])
        self.executor = StudentCodeExecutor(self.config, self.match_pipe[0])
        self.executor.start()

    async def get_match(self, _request):
        async with self.access:
            return self.match.as_dict()

    async def set_match(self, request: dict):
        """ Set the match information. """
        async with self.access:
            self.match.alliance, self.match.mode = request['alliance'], request['mode']
            self.match_pipe[1].send(self.match)
            return self.match.as_dict()

    async def run_challenge(self, request: dict):
        self.executor.reload_student_code(self.match)
        seed = request['seed']
        challenges = [getattr(self.executor.student_code, challenge)
                      for challenge in request['challenges']]
        with ProcessPoolExecutor() as executor:
            loop = asyncio.get_running_loop()
            answer = await loop.run_in_executor(executor, run_challenge, challenges, seed)
            LOGGER.info('Completed coding challenge', seed=seed, answer=answer,
                        challenges=request['challenges'])
            # Serialize as a string, since the answer may exceed the capacity of an unsigned long.
            return {'answer': str(answer)}

    async def list_aliases(self, _request):
        async with self.access:
            return {'aliases': dict(self.aliases.data)}

    async def set_alias(self, request):
        async with self.access:
            alias = request['alias']
            self.aliases[alias['name']] = alias['uid']
            return {'aliases': dict(self.aliases.data)}

    async def del_alias(self, request):
        async with self.access:
            del self.aliases[request['alias']['name']]
            return {'aliases': dict(self.aliases.data)}

    async def lint(self):
        raise NotImplemented

    async def main(self):
        command_conn = self.connections.command
        while True:
            request, response = await command_conn.recv(), {'received': time.time()}
            LOGGER.info('Received request', **request)
            try:
                request = self.request_schema.validate(request) or {}
                command = getattr(self, request['type'].name.lower())
                response.update(await command(request) or {})
            except SchemaError as exc:
                response['exc'] = str(exc)
                LOGGER.error('Received bad command, treating as no-op')
            except RuntimeBaseException as exc:
                response['exc'] = str(exc)
                response.update(exc.context)
                LOGGER.error('Unable to execute command')
            finally:
                response['completed'] = time.time()
                # TODO: clean up nested try/except logic
                try:
                    await command_conn.send(response)
                except OverflowError:
                    await command_conn.send({})
                LOGGER.debug('Sent response', **response)
                response.clear()
