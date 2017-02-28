# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: runtime.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='runtime.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\rruntime.proto\"\xb8\x03\n\x0bRuntimeData\x12\'\n\x0brobot_state\x18\x01 \x01(\x0e\x32\x12.RuntimeData.State\x12,\n\x0bsensor_data\x18\x02 \x03(\x0b\x32\x17.RuntimeData.SensorData\x1aO\n\nParamValue\x12\r\n\x05param\x18\x01 \x01(\t\x12\x15\n\x0b\x66loat_value\x18\x02 \x01(\x02H\x00\x12\x13\n\tint_value\x18\x03 \x01(\x05H\x00\x42\x06\n\x04kind\x1a\x97\x01\n\nSensorData\x12\x13\n\x0b\x64\x65vice_type\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65vice_name\x18\x02 \x01(\t\x12\x0b\n\x03uid\x18\x04 \x01(\x04\x12\x17\n\x0fint_device_type\x18\x05 \x01(\r\x12,\n\x0bparam_value\x18\x06 \x03(\x0b\x32\x17.RuntimeData.ParamValueJ\x04\x08\x03\x10\x04R\x05value\"g\n\x05State\x12\x13\n\x0fSTUDENT_CRASHED\x10\x00\x12\x13\n\x0fSTUDENT_RUNNING\x10\x01\x12\x13\n\x0fSTUDENT_STOPPED\x10\x02\x12\n\n\x06TELEOP\x10\x03\x12\x08\n\x04\x41UTO\x10\x04\x12\t\n\x05\x45STOP\x10\x05\x62\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_RUNTIMEDATA_STATE = _descriptor.EnumDescriptor(
  name='State',
  full_name='RuntimeData.State',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='STUDENT_CRASHED', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STUDENT_RUNNING', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STUDENT_STOPPED', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TELEOP', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='AUTO', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ESTOP', index=5, number=5,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=355,
  serialized_end=458,
)
_sym_db.RegisterEnumDescriptor(_RUNTIMEDATA_STATE)


_RUNTIMEDATA_PARAMVALUE = _descriptor.Descriptor(
  name='ParamValue',
  full_name='RuntimeData.ParamValue',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='param', full_name='RuntimeData.ParamValue.param', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='float_value', full_name='RuntimeData.ParamValue.float_value', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='int_value', full_name='RuntimeData.ParamValue.int_value', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='kind', full_name='RuntimeData.ParamValue.kind',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=120,
  serialized_end=199,
)

_RUNTIMEDATA_SENSORDATA = _descriptor.Descriptor(
  name='SensorData',
  full_name='RuntimeData.SensorData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='device_type', full_name='RuntimeData.SensorData.device_type', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='device_name', full_name='RuntimeData.SensorData.device_name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='uid', full_name='RuntimeData.SensorData.uid', index=2,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='int_device_type', full_name='RuntimeData.SensorData.int_device_type', index=3,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='param_value', full_name='RuntimeData.SensorData.param_value', index=4,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=202,
  serialized_end=353,
)

_RUNTIMEDATA = _descriptor.Descriptor(
  name='RuntimeData',
  full_name='RuntimeData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='robot_state', full_name='RuntimeData.robot_state', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sensor_data', full_name='RuntimeData.sensor_data', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_RUNTIMEDATA_PARAMVALUE, _RUNTIMEDATA_SENSORDATA, ],
  enum_types=[
    _RUNTIMEDATA_STATE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=18,
  serialized_end=458,
)

_RUNTIMEDATA_PARAMVALUE.containing_type = _RUNTIMEDATA
_RUNTIMEDATA_PARAMVALUE.oneofs_by_name['kind'].fields.append(
  _RUNTIMEDATA_PARAMVALUE.fields_by_name['float_value'])
_RUNTIMEDATA_PARAMVALUE.fields_by_name['float_value'].containing_oneof = _RUNTIMEDATA_PARAMVALUE.oneofs_by_name['kind']
_RUNTIMEDATA_PARAMVALUE.oneofs_by_name['kind'].fields.append(
  _RUNTIMEDATA_PARAMVALUE.fields_by_name['int_value'])
_RUNTIMEDATA_PARAMVALUE.fields_by_name['int_value'].containing_oneof = _RUNTIMEDATA_PARAMVALUE.oneofs_by_name['kind']
_RUNTIMEDATA_SENSORDATA.fields_by_name['param_value'].message_type = _RUNTIMEDATA_PARAMVALUE
_RUNTIMEDATA_SENSORDATA.containing_type = _RUNTIMEDATA
_RUNTIMEDATA.fields_by_name['robot_state'].enum_type = _RUNTIMEDATA_STATE
_RUNTIMEDATA.fields_by_name['sensor_data'].message_type = _RUNTIMEDATA_SENSORDATA
_RUNTIMEDATA_STATE.containing_type = _RUNTIMEDATA
DESCRIPTOR.message_types_by_name['RuntimeData'] = _RUNTIMEDATA

RuntimeData = _reflection.GeneratedProtocolMessageType('RuntimeData', (_message.Message,), dict(

  ParamValue = _reflection.GeneratedProtocolMessageType('ParamValue', (_message.Message,), dict(
    DESCRIPTOR = _RUNTIMEDATA_PARAMVALUE,
    __module__ = 'runtime_pb2'
    # @@protoc_insertion_point(class_scope:RuntimeData.ParamValue)
    ))
  ,

  SensorData = _reflection.GeneratedProtocolMessageType('SensorData', (_message.Message,), dict(
    DESCRIPTOR = _RUNTIMEDATA_SENSORDATA,
    __module__ = 'runtime_pb2'
    # @@protoc_insertion_point(class_scope:RuntimeData.SensorData)
    ))
  ,
  DESCRIPTOR = _RUNTIMEDATA,
  __module__ = 'runtime_pb2'
  # @@protoc_insertion_point(class_scope:RuntimeData)
  ))
_sym_db.RegisterMessage(RuntimeData)
_sym_db.RegisterMessage(RuntimeData.ParamValue)
_sym_db.RegisterMessage(RuntimeData.SensorData)


# @@protoc_insertion_point(module_scope)
