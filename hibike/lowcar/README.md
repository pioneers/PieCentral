# The lowcar library #

Links to third party libraries

### How to add a new device: ###
1) Create a new header file, and name it with the new device name
	- In this header file, create a class that is derived from the Device base class for the new device
	- Specify which of the five virtual functions you need to override
	- Declare any private variables you may need for the device
	- Include any third-party libraries you need
2) Create a new folder that has the same name as the device
3) Within that folder, create a source file that has the name as the device
	- Write the implementations of the functions that need to be overridden in this file
	- Create helper classes if needed. Both header and source files of helper classes should stay within the device-specific folder

Explanations of code / how to use / how to flash etc