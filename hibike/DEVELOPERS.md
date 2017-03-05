# Documentation for hibike developers

## Documentation for adding/modifying device firmware

### Hibike Device Abstraction

Hibike abstracts all devices as a dictionary of param -> value mappings.
Some params, like a potentiometer reading, will be read-only, whereas others, like a servo angle, can be written to as well.

A Hibike Device Type is defined by the following

 - Device Name
 - Device ID number
 - For each paramater of the device
   - Param Name
   - Param Type (bool uint16_t float etc.)
   - Is the Param readable?
   - Is the Param writeable?

Hibike Devices Type definitions are listed in a table in hibike/README.md, as well as in hibike/hibikeDevices.json

### To add a new device type definition or modify the definition of an existing device type

 - Add/Update the corresponding entries to hibike/hibikeDevices.json hibike/README.md

### Writing Hibike Device Firmware

Look at hibike/devices/ExampleDevice for an example implementation of a hibike device

Device specific firmware must:

 - Implement the arduino setup() and loop() functions, which must call hibike_setup() and hibike_loop() correspondingly
 - Implement device_write() and device_data_update(), which are called when the BBB wants to either write to the device or get a data update from the device. 
   - Both functions are given with a buffer containing data and a param index. Because params can have different data types and therefore values with different sizes, these functions must return the number of bytes they read from/wrote to their buffer.
   - Both functions are given the size of the buffer to avoid overflow. They must return 0 if their normal operation would overflow the buffer.
 - Conform to their device type definition described in hibikeDevices.json
 - Have the uid in their .h file filled out correctly
   - The uid references the device type id, which by convention is defined in an enum in hibike/lib/hibike/devices.h
 - Call hibike_loop() at a higher frequency than both
   - The expected frequency of the BBB sending packets to the device
   - The expected subscription frequency (The BBB will subscribe to device data updates at some frequency)

### Using libraries in device firmware

For standard arduino libraries like <Servo.h> or <SPI.h>:

 - go to hibike/Makefile and update the line that looks starts with `ARDUINO_LIBS :=`

For external libraries:

 - add the library folder to hibike/lib
   - see the libraries already there
 - go to hibike/Makefile and update the line that looks starts with `SKETCH_LIBS =`
 