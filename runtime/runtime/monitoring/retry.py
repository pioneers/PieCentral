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
from schema import And, Schema, Optional, Use


def make_retry_strategy(retry_config) -> Callable:
    pass
