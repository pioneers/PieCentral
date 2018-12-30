import asyncio
from collections import UserDict
from enum import IntEnum
import functools
import os
import json
import re
import signal
import threading
import time
import yaml


class RuntimeBaseException(UserDict, Exception):
    """
    Base class for Runtime-specific exceptions.

    Unlike built-in Exceptions, ``RuntimeBaseException`` accepts arbitrary data
    that can be examined in post-mortems or written into structured logs.

    Example:

        >>> err = RuntimeBaseException('Error', input=1, valid=[2, 3])
        >>> err['input']
        1
        >>> err['valid']
        [2, 3]
    """
    def __init__(self, msg: str, **data):
        super().__init__(data)
        super(Exception, self).__init__(msg)

    def __repr__(self):
        cls_name, (msg, *_) = self.__class__.__name__, self.args
        if self:
            kwargs = ', '.join(f'{name}={repr(value)}' for name, value in self.items())
            return f'{cls_name}({repr(msg)}, {kwargs})'
        return f'{cls_name}({repr(msg)})'


class RuntimeIPCException(RuntimeBaseException):
    pass


class RuntimeExecutorException(RuntimeBaseException):
    pass


class AutoIntEnum(IntEnum):
    """
    An enum with automatically incrementing integer values, starting from zero.

    References:
        .. _Python `enum` Reference
            https://docs.python.org/3/library/enum.html#using-automatic-values
    """
    # pylint: disable=no-self-argument
    def _generate_next_value_(name, start, count, last_values):
        return count


CONF_FILE_FORMATS = {
    re.compile(r'\.(yml|yaml)', flags=re.IGNORECASE): (yaml.load, yaml.dump),
    re.compile(r'\.json', flags=re.IGNORECASE): (json.load, json.dump),
}


@functools.lru_cache()
def get_conf_file_serializer(filename: str):
    _, extension = os.path.splitext(filename)
    for ext_pattern, serializer in CONF_FILE_FORMATS.items():
        if ext_pattern.match(extension):
            return serializer
    raise RuntimeBaseException('Configuration file format not recognized.',
                               extension=extension, valid_formats=list(CONF_FILE_FORMATS))


def read_conf_file(filename: str):
    """
    Read and parse a configuration file.

    Example:

        >>> read_conf_file('badformat.csv')
        Traceback (most recent call last):
          ...
        runtime.util.RuntimeBaseException: Configuration file format not recognized.
    """
    load, _ = get_conf_file_serializer(filename)
    with open(filename) as conf_file:
        try:
            return load(conf_file)
        except Exception as exc:
            # Standardize exception types raised by third-party parsers.
            raise RuntimeBaseException(
                'Unable to parse configuration file.',
                filename=filename,
            ) from exc


def write_conf_file(filename: str, data):
    """ Serialize and write a configuration file. """
    _, dump = get_conf_file_serializer(filename)
    with open(filename, 'w+') as conf_file:
        try:
            return dump(data, conf_file)
        except Exception as exc:
            # Standardize exception types raised by third-party parsers.
            raise RuntimeBaseException(
                'Unable to serialize data for configuration file.',
                filename=filename,
            ) from exc


class AsyncThread(threading.Thread):
    def __init__(self, *thread_args, target=None, args=None, kwargs=None,
                 cleanup_timeout=5, **thread_kwargs):
        args, kwargs = args or (), kwargs or {}
        if target:
            self.target, self.args, self.kwargs = target, args, kwargs
            target, args, kwargs = self.bootstrap, (), {}
            self.cleanup_timeout = cleanup_timeout
        super().__init__(*thread_args, **thread_kwargs, target=target, args=args, kwargs=kwargs)

    def bootstrap(self):
        self.loop = asyncio.new_event_loop()
        self.task = self.loop.create_task(self.target(*self.args, **self.kwargs))
        try:
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.task)
        except asyncio.CancelledError:
            pass
        finally:
            tasks = asyncio.all_tasks(self.loop)
            for task in tasks:
                if not task.cancelled():
                    self.loop.call_soon_threadsafe(task.cancel)
            tasks = asyncio.gather(*tasks, return_exceptions=True)
            tasks = asyncio.wait_for(tasks, self.cleanup_timeout)
            self.loop.run_until_complete(tasks)
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.stop()
            self.loop.close()

    def run(self):
        if hasattr(self, 'loop') and self.loop.is_running():
            raise OSError('AsyncioThread is already running.')
        super().run()

    def stop(self):
        if hasattr(self, 'loop') and hasattr(self, 'task'):
            if self.loop.is_running():
                self.loop.call_soon_threadsafe(self.task.cancel)


class AsyncTimer:
    def __init__(self, callback, delay, args=None, kwargs=None):
        self.callback, self.delay = callback, delay
        self.args, self.kwargs = args or (), kwargs or {}
        self.halt = asyncio.Event()

    async def run(self):
        start, tick = time.time(), 0
        while not self.halt.is_set():
            tick += 1
            end = start + self.delay*tick
            try:
                stop = await asyncio.wait_for(self.callback(*self.args, **self.kwargs), self.delay)
                if stop:
                    self.stop()
            except asyncio.TimeoutError:
                pass  # TODO: LOGGER.warn('')
            else:
                delay = end - time.time()
                if delay > 0:
                    await asyncio.sleep(delay)

    def stop(self):
        self.halt.set()


def handle_async_termination(_signum, _stack_frame):
    for task in asyncio.all_tasks():
        task.cancel()


def wrap_async_main(async_main):
    @functools.wraps(async_main)
    def main(*args, **kwargs):
        signal.signal(signal.SIGTERM, handle_async_termination)
        return asyncio.run(async_main(*args, **kwargs))
    return main
