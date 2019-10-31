"""
Retryable proxies.
"""

import abc
import asyncio
import collections
import dataclasses
import functools
import inspect
from typing import Any, Callable, Generic, Mapping, Optional, TypeVar

import backoff
import cachetools
from cachetools.keys import hashkey
import structlog

Resource = TypeVar('Resource')


@dataclasses.dataclass
class Proxy(abc.ABC, Generic[Resource]):
    policies: Mapping[str, Callable]
    resource: Optional[Resource] = dataclasses.field(init=False)

    def __post_init__(self):
        for name, policy in self.policies.items():
            method = getattr(self, name)
            setattr(self, name, policy(method, on_backoff=self.retry_resource))

    def __enter__(self):
        self.resource = self.initialize_resource()
        return self

    def __exit__(self, *_):
        self.terminate_resource(self.resource)

    @abc.abstractmethod
    def initialize_resource(self) -> Resource:
        pass

    @abc.abstractmethod
    def terminate_resource(self, resource: Resource):
        pass

    def retry_resource(self):
        if self.resource is not None:
            self.terminate_resource(self.resource)
        self.resource = self.initialize_resource()
