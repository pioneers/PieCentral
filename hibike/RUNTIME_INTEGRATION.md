# Hibike Runtime Integration

All hibike smart devices are abstracted as a mapping of parameters to values.
Runtime can read from, write to, or subscribe to these parameters.
Paramaters are always strings, but the type of each value is unique.
A config file will describe the type of the value for each paramater, and the parameters for each smart device type.
A parameter can be read only, write only, or read/write.

## Example Smart Devices:

LimitSwitch

- switch0: bool read only
- switch1: bool read only
- switch2: bool read only
- switch2: bool read only

Servo

- servo0_torqued: bool read/write
- servo0_pos: int read/write

MetalDetector

- calibrate: bool write only
- reading: int read only



## StateManager -> Hibike

`["enumerate_all", []]`

- tells hibike to reenumerate all smart devices

`["subscribe_device", [uid, delay, [param1, param2, ...]]]`

- tells hibike to subscribe to specific paramaters of a smart device

`["write_params", [uid, [(param1, value1), (param2, value2)...]]]`

- tells hibike to write to specific paramaters of a smart device

`["read_params", [uid, [param1, param2, ...]]`

- tells hibike to read (poll) specific paramaters of a smart device

`["disable_all",[]]`

- tells hibike to disable all devices.  Consult README.md to explain what disable does.



## Hibike -> StateManager

`["device_subscribed", [uid, delay, [param1, param2, ...]]]`

- sent when the BBB either enumerates or subscribes to a smart device

`["device_disconnected", [uid]]`

- sent when a smart device disconnects

`["device_values", [uid, [(param1, value1), (param2, value2)...]]]`

- sent when the BBB receives values from a smart device

`["invalid_uid", [uid]]`

- sent when hibike receives a command from stateManager with a smart device that isn't connected

`["invalid_param", [uid, param]]`

- sent when hibike receives a command for a valid uid with a nonexistent param

`["param_read_only", [uid, param]]`

- sent when stateManager tries to write to a read only param

`["param_write_only", [uid, param]]`

- sent when stateManager tries to poll or subscribe to a write only param

`["device_disconnect", [uid]]`

- sent when a device disconnects from Hibike
