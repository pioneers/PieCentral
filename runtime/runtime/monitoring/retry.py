"""
Retryable proxies.
"""

import asyncio
import collections
import dataclasses
import functools
import inspect
from typing import Any, Callable, Mapping

import backoff
import cachetools
from cachetools.keys import hashkey
import structlog


Policies = Mapping[str, Callable]


@dataclasses.dataclass
class Proxy:
    """
    Example::

        >>> import logging
        >>> fail_counter = 0
        >>> class Resource:
        ...     def add(self, a, b):
        ...         return a + b
        ...     def sub(self, a, b):
        ...         global fail_counter
        ...         fail_counter += 1
        ...         if fail_counter <= 2:
        ...             raise ValueError('transient failure')
        ...         return a - b
        ...     def mul(self, a, b):
        ...         raise ValueError('invalid operation')
        >>> policy = functools.partial(backoff.on_exception, backoff.constant,
        ...                            ValueError, max_tries=3, interval=0)
        >>> policies = {'sub': policy, 'mul': policy}
        >>> resource = Proxy(Resource, logging.getLogger(), policies)
        >>> resource.add(1, 2)
        3
        >>> resource.sub(1, 2)
        -1
        >>> resource.mul(1, 2)
        Traceback (most recent call last):
          ...
        ValueError: invalid operation
        >>> resource.div
        Traceback (most recent call last):
          ...
        AttributeError: 'Resource' object has no attribute 'div'
    """
    factory: Callable
    logger: structlog.BoundLoggerBase = dataclasses.field(default_factory=structlog.get_logger)
    policies: Policies = dataclasses.field(default_factory=collections.defaultdict)
    cleanup: Callable = lambda _resource: None
    resource: Any = dataclasses.field(default=None, init=False)

    @property
    def _resource(self):
        """ Get or create an instance of the resource. """
        if self.resource is None:
            self.resource = self.factory()
        return self.resource

    def _clear_resource(self, _debug=None):
        """ Clean up the resource and allow a new one to be created. """
        if self.resource is not None:
            self.cleanup(self.resource)
        self.resource = None

    @cachetools.cached(cache={}, key=lambda _, name: hashkey(name))
    def _wrap_method(self, name: str):
        """
        Make a retryable version of a method on the resource.

        Note::
            The method, once built, is cached by its name.
        """
        policy = self.policies[name]
        method = getattr(self._resource, name)
        if not policy:
            return method
        policy = policy(logger=self.logger, on_backoff=self._clear_resource)

        if inspect.iscoroutinefunction(method):
            @policy
            @functools.wraps(method)
            async def wrapper(*args, **kwargs):
                method = getattr(self._resource, name)
                return await method(*args, **kwargs)
        else:
            @policy
            @functools.wraps(method)
            def wrapper(*args, **kwargs):
                method = getattr(self._resource, name)
                return method(*args, **kwargs)
        return wrapper

    def __getattr__(self, name: str):
        # Methods on `RetryProxy` itself have priority in the lookup.
        if name in self.__dict__:
            return self.__dict__[name]
        attr = getattr(self._resource, name)
        if not inspect.ismethod(attr):
            return attr
        else:
            return self._wrap_method(name)
