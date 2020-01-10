import collections
import ctypes
import dataclasses
from multiprocessing.shared_memory import SharedMemory
from multiprocessing.managers import SharedMemoryManager
import time

import cachetools
import zmq
from runtime.util.exception import RuntimeBaseException


@cachetools.cached(cache={})
def make_timestamped_parameter(param_type) -> type:
    class TimestampedParameter(ctypes.Structure):
        _fields_ = [
            ('value', param_type),
            ('last_updated', ctypes.c_double),
        ]

        def __setattr__(self, name: str, value):
            if name == 'value':
                self.last_updated = time.time()
            # TODO: validate parameter bounds?
            super().__setattr__(name, value)
    return TimestampedParameter


class SmartSensorUID(ctypes.Structure):
    _fields_ = [
        ('device_type', ctypes.c_uint16),
        ('year', ctypes.c_uint8),
        ('id', ctypes.c_uint64),
    ]


class DeviceStructure(ctypes.Structure):
    """
    The state of a device with readable/writeable parameters.

    Note::
        A "device" is more general than a "Smart Sensor", which is a special
        kind of "device". For example, gamepads are also treated as "devices".
    """
    Parameter = collections.namedtuple(
        'Parameter',
        ['name', 'type', 'lower', 'upper', 'readable', 'writeable'],
        defaults=[float('-inf'), float('inf'), True, False],
    )

    @classmethod
    def make_type(cls: type, name: str, type_id: int, params: List[Parameter], *extra_fields):
        fields = list(extra_fields)
        for param in params:
            ctype = make_timestamped_parameter(param.type)
            fields.extend([(f'current_{param.name}', ctype), (f'desired_{param.name}', ctype)])
        return type(name, (cls, ), {
            '_params': {param.name: param for param in params},
            '_fields_': fields,
            'type_id': type_id,
        })

    @classmethod
    def make_smart_sensor_type(cls: type, name: str, type_id: int, params: List[Parameter]):
        """
        Make a device type with extra fields to handle the Smart Sensor protocol.

        The extra fields included are:
          * `dirty`: A bitmap used to see what parameters have been written to
            since the last device write.
          * `delay`: The current subscription period.
          * `subscription`: A bitmap of the parameters the Smart Sensor consumer
            is subscribed to.
          * `uid`: The unique identifier of the Smart Sensor.
        """
        if len(params) > 16:
            raise RuntimeBaseException('Maxmimum number of Smart Sensor parameters exceeded')
        extra_fields = [
            ('dirty', ctypes.c_uint16),
            ('delay', ctypes.c_uint16),
            ('subscription', ctypes.c_uint16),
            ('uid', SmartSensorUID),
        ]
        return DeviceStructure.make_type(name, type_id, params, *extra_fields)


VALID_NAME = Regex(r'^[a-zA-Z_]\w*$')
DEVICE_SCHEMA = Schema({
    And(Use(str), VALID_NAME): {        # Protocol name
        And(Use(str), VALID_NAME): {    # Device name
            'id': And(Use(int), lambda type_id: 0 <= type_id < 0xFFFF),
            'params': [{
                'name': Use(str),
                'type': And(Use(str), Use(lambda: dev_type: getattr(ctypes, f'c_{dev_type}'))),
                Optional('lower'): Use(float),
                Optional('upper'): Use(float),
                Optional('readable'): Use(bool),
                Optional('writeable'): Use(bool),
            }]
        }
    }
})


@dataclasses.dataclass
class Device:
    buffer: ctypes.Structure
    send: Callable
    recv: Callable

    device_types = {}
    smart_sensor_protocol_name = 'smartsensor'

    @classmethod
    def load_device_types(cls: type, schema):
        """ Populate the device type registry from a raw device schema. """
        schema = DEVICE_SCHEMA.validate(schema)
        cls.device_types.clear()
        for protocol, devices in schema.items():
            cls.device_types[protocol] = {}
            if protocol == cls.smart_sensor_protocol_name:
                make_device_type = DeviceStructure.make_smart_sensor_type
            else:
                make_device_type = DeviceStructure.make_device_type
            for device_name, device_conf in devices.items():
                params = [DeviceStructure.Parameter(*param_conf)
                          for param_conf in device_conf['params']]
                cls.device_types[protocol][device_name] = make_device_type(
                    device_name, device_conf['id'], params)

    def ping(self):
        pass

    def request_subscription(self):
        pass

    def request_heartbeat(self):
        pass


"""
class DeviceStructure(ctypes.LittleEndianStructure):
    Parameter = collections.namedtuple(
        'Parameter',
        ['name', 'type', 'lower', 'upper', 'readable', 'writeable'],
        defaults=[float('-inf'), float('inf'), True, False],
    )
    timestamp_type = ctypes.c_double

    @staticmethod
    def _get_timestamp_name(param: str) -> str:
        return f'{param}_ts'

    def __setattr__(self, name: str, value):
        param = self._params[name]
        if isinstance(value, numbers.Real):
            if not param.lower <= value <= param.upper:
                raise RuntimeBaseException(
                    'Invalid value assigned to device parameter',
                    cause='invalid-bounds',
                    value=value,
                    lower=param.lower,
                    upper=param.upper,
                    param_name=param.name,
                    dev_name=self.__class__.__name__,
                )
"""
#
#
# @dataclasses.dataclass(init=False)
# class Device:
#     def __init__(self, struct: type, read_buf: SharedMemory, write_buf: SharedMemory):
#         self.struct, self.read_buf, self.write_buf = struct, read_buf, write_buf
#         self.read_struct = struct.from_buffer(self.read_buf)
#         self.write_struct = struct.from_buffer(self.write_buf)
#
#     @staticmethod
#     def open_device(struct: type, read_buf_name: str, write_buf_name: str):
#         """ Open a device with existing shared memory buffers. """
#         return Device(struct, SharedMemory(read_buf_name), SharedMemory(write_buf_name))
#
#     @staticmethod
#     def create_device(shm_manager: SharedMemoryManager, struct: type):
#         """ Create a device with new shared memory buffers. """
#         size = ctypes.sizeof(struct)
#         read_buf = shm_manager.SharedMemory(size)
#         write_buf = shm_manager.SharedMemory(size)
#         return Device(struct, read_buf, write_buf)
#
#     def close(self):
#         self.read_buf.close()
#         self.write_buf.close()
#
#     def __getattr__(self, name: str):
#         param = self.struct._params.get(name)
#         if param is not None:
#             if param.readable:
#                 return getattr(self.read_struct, name)
#             else:
#                 raise RuntimeBaseException('Parameter is not readable')
#         else:
#             raise AttributeError
#
#     def __setattr__(self, name: str, value):
#         param = self.struct._params.get(name)
#         if param is not None:
#             if param.writeable:
#                 setattr(self.write_struct, name, value)
#             else:
#                 raise RuntimeBaseException('Parameter is not writeable')
#         else:
#             super().__setattr__(name, value)
#
#
# @dataclasses.dataclass
# class DeviceManager:
#     publisher: zmq.Socket
#     subscriber: zmq.Socket
#     device_id: Mapping[str, Device]
