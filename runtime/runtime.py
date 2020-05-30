import abc
import asyncio
import collections
import ctypes
import dataclasses
from multiprocessing.shared_memory import SharedMemory
import threading
import uuid

import aioserial
import click
import pyudev
import typing
from serial.tools import list_ports
import structlog

LOGGER = structlog.get_logger()


class FrameControl(StructureBase):
    _fields_ = [
        ('write', ctypes.c_uint16),
        ('read', ctypes.c_uint16),
    ]


class DawnProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        print(exc)

    def datagram_received(self, data, address):
        print(address)

    def error_received(self, exc):
        pass


class Device(abc.ABC):
    @abc.abstractmethod
    async def spin(self):
        pass


@dataclasses.dataclass
class Device:
    serial_conn: aioserial.AioSerial


@click.command()
def cli(**options):
    Frame.register_type('YogiBear', 1, [])
    frame = Frame.open(1, '123', create=True)


if __name__ == '__main__':
    cli()
