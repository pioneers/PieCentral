import collections
import ctypes
from multiprocessing.shared_memory import SharedMemory
from numbers import Real
from schema import And, Optional, Schema, Use
import typing

import structlog

from runtime.service.storage import Document
from runtime.util import VALID_NAME
from runtime.util.exception import RuntimeBaseException


class StructureBase(ctypes.LittleEndianStructure):
    """
    The Smart Sensor protocol uses little Endian byte order (least-significant byte first).
    """
    def __repr__(self):
        fields = ', '.join(f'{name}={getattr(self, name)!r}' for name, _ in self._fields_)
        return f'{self.__class__.__name__}({fields})'


class Parameter(typing.NamedTuple):
    name: str
    type: type
    lower: Real = float('-inf')
    upper: Real = float('inf')
    readable: bool = True
    writeable: bool = False
    subscribed: bool = False


class SensorUID(StructureBase):
    """
    A Smart Sensor Unique Identifer (UID).

    The UID is effectively a 96-bit integer that encodes Sensor metadata:
      * `type_id`: An integer denoting the type of Sensor. The types are
            given by the Smart Sensor protocol specification.
      * `year`: The year the Sensor is from. 2016 is denoted as year zero.
      * `id`: A randomly generated ID. This ensures the probability of a UID
            collision (two devices of the same type from the same year) is
            negligible.
    """
    _pack_ = 1  # Ensure the fields are byte-aligned (pack as densely as possible)
    _fields_ = [
        ('type_id', ctypes.c_uint16),
        ('year', ctypes.c_uint8),
        ('id', ctypes.c_uint64),
    ]

    def __str__(self):
        return str(self.to_int())

    def to_int(self) -> int:
        """
        Return an integer representation of this UID.

        Warning::
            Serializing the UID as an integer may fail if the serializer cannot
            represent integers larger than 64 bits (UID is 96 bits).
        """
        return (self.type_id << 72) | (self.year << 64) | self.id


class SensorControl(StructureBase):
    _fields_ = [
        ('uid', SensorUID),
        ('write', ctypes.c_uint16),
        ('read', ctypes.c_uint16),
        ('delay', ctypes.c_uint16),
        ('subscription', ctypes.c_uint16),
        ('timestamp', ctypes.c_double),
    ]


class Catalog(collections.UserDict):
    catalog_schema: typing.ClassVar[Schema] = Schema({
        And(Use(str), VALID_NAME): {        # Protocol name
            And(Use(str), VALID_NAME): {    # Device name
                'type_id': And(Use(int), lambda type_id: 0 <= type_id < 0xFFFF),
                Optional('delay'): Use(float),
                'params': [And({
                    'name': Use(str),
                    'type': And(Use(str), Use(lambda dev_type: getattr(ctypes, f'c_{dev_type}'))),
                    Optional('lower'): Use(float),
                    Optional('upper'): Use(float),
                    Optional('readable'): Use(bool),
                    Optional('writeable'): Use(bool),
                    Optional('subscribed'): Use(bool),
                }, Use(lambda param: Parameter(**param)))]
            }
        },
    })

    def __setitem__(self, type_id: int, frame_type: type):
        existing_type = super().get(type_id)
        if existing_type:
            raise RuntimeBaseException(
                'Catalog already contains device type ID',
                type_id=type_id,
                name=frame_type.__name__,
                existing_name=existing_type.__name__,
            )
        super().__setitem__(type_id, frame_type)

    async def load(self, catalog: Document):
        await catalog.load()
        protocols = self.catalog_schema.validate(await catalog.get())
        for protocol, devices in protocols.items():
            for name, device in devices.items():
                frame_type = SensorFrame if protocol == SensorFrame.protocol else Frame
                self[device['type_id']] = frame_type.make_type(name=name, **device)


class Frame(StructureBase):
    """
    A frame is a buffer of device state backed by shared memory.
    """
    catalog = Catalog()

    @classmethod
    def make_type(cls, name: str, type_id: int, params: typing.Sequence[Parameter],
                  *extra_fields: typing.Tuple[str, type]) -> type:
        readable_fields = [(param.name, param.type) for param in params if param.readable]
        writeable_fields = [(param.name, param.type) for param in params if param.writeable]
        read_type = type(f'{name}ReadBlock', (StructureBase,), {'_fields_': readable_fields})
        write_type = type(f'{name}WriteBlock', (StructureBase,), {'_fields_': writeable_fields})
        fields = [('read', read_type), ('write', write_type), *extra_fields]
        return type(name, (cls,), {'type_id': type_id, 'params': params, '_fields_': fields})

    @classmethod
    def open(cls, type_id: int, uid: str, create: bool = False):
        device_type = cls.catalog[type_id]
        name = f'{device_type.__name__.lower()}-{uid}'
        try:
            shm = SharedMemory(name, create=create, size=ctypes.sizeof(device_type))
        except FileNotFoundError as exc:
            raise RuntimeBaseException('Cannot attach to nonexistent shared memory', **context) from exc
        except FileExistsError:
            shm = SharedMemory(name)
        frame = device_type.from_buffer(shm.buf)
        frame.create, frame.shm = create, shm
        return frame

    def __del__(self):
        # This hack is needed so that the reference count on the shared memory
        # buffer goes to zero and the buffer can be freed. Otherwise, a
        # `_shm.close` will throw a `BufferError` because the exported pointer
        # hiding in `_objects` would point to garbage memory.
        if isinstance(self._objects, dict):
            self._objects.clear()

        self.shm.close()
        if self.create:
            self.shm.unlink()

    def __getitem__(self, param: str):
        return getattr(self.read, param)

    def __setitem__(self, param: str, value):
        setattr(self.write, param, value)


class SensorFrame(Frame):
    max_params: int = 16
    protocol: str = 'smartsensor'
    reset_parameters: int = 0x0000

    @classmethod
    def make_type(cls, name: str, type_id: int, delay: Real,
                  params: typing.Sequence[Parameter]) -> type:
        if len(params) > cls.max_params:
            raise RuntimeBaseException('Sensor has too many parameters', params=len(params),
                                       max_params=cls.max_params)
        device_type = super().make_type(name, type_id, params, ('control', SensorControl))
        device_type.delay = delay
        return device_type

    @classmethod
    def from_bitmap(cls, bitmap: int) -> typing.Generator[Parameter, None, None]:
        """ Translate a parameter bitmap into parameters. """
        for index, param in enumerate(cls.params):
            if (bitmap >> index) & 0b1:
                yield param

    @classmethod
    def to_bitmap(cls, params: typing.Container[str]) -> int:
        bitmap = 0
        for index, param in enumerate(cls.params):
            if param.name in params:
                bitmap |= 1 << index
        return bitmap

    def reset(self):
        raise NotImplemented

    @property
    def subscription(self) -> typing.Generator[Parameter, None, None]:
        return self.from_bitmap(self.control.subscription)
