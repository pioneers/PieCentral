# Virtual Hibike Devices

Hibike features virtual devices, which attempt to simulate the behavior of real hibike devices for testing purposes.

Virtual devices expose a serial interface similar to the ones exposed by real hibike devices

## Usage

### TL;DR

dependencies:
 - socat
 - python3
 - pyserial for python3

edit line 10 of spawn_virtual_devices.py to configure what devices you want and run it with python3

### socat

In order to expose a serial interface, virtual devices use the command line utility `socat`.
You must install socat in order to use virtual devices.

Socat essentially generates a pair of connected virtual serial ports. Anything written to one of these ports can be read from the other. This way, the virtual device program can connect to one end of the pair of serial ports, and a program that wishes to communicate with hibike devices, such as `hibike_process.py`, can connect to the other end.

The call we make to spawn a pair of ports is socat is `socat -d -d pty,raw,echo=0 pty,raw,echo=0`.

### virtual_device.py

The python script virtual_device.py simulates a hibike_device.
It takes in as command line arguments the type of device to emulate and a port to connect to.
It has an external dependency on pyserial and should be run with python3.

If you wish to implement more virtual devices types, or change the behaviour of any of the virtual device types, this is the file to modify.

### spawn_virtual_devices.py

This is a helper script that runs multiple instances of the previous two programs, socat and virtual_device.py, to generate multiple virtual hibike devices.
Furthermore, it collects all the virtual serial ports for communicating with these devices into the file `virtual_devices.txt`, which programs like `hibike_process.py` read to know where virtual_devices are.

It also has an atexit handler that should clean up these child processes, though this may not always happen, for example if `spawn_virtual_devices.py` is killed with SIGKILL.

`spawn_virtual_devices.py` currently hardcodes a list of devices to spawn in line 10. This can be edited to any desired list of devices. The currently supported device types are `LimitSwitch`, `ServoControl`, and `Potentiometer`. Though code for `YogiBear` exists and works, the YogiBear team is currently developing YogiBear firmware with a different set of paramaters, so the use of this virtual device type is not recommended until YogiBear firmware is finalized and the virtual device is updated to match this.