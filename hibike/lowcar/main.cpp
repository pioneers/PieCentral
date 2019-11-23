#include "Device.h"
#include "LimitSwitch.h"
#include "LineFollower.h"
#include "RFID.h"
#include "ServoControl.h"

/* This main file should be as simple as possible.
 * Every device runs this main file.
 * All device-specific behaviors are encapsulated by 
 * the Device class and its derived classes.
 */

Device *device; //declare the device

void setup()
{
	//this is going to get replaced by whatever device the user specified upon running the flash script
	device = new DEVICE(); // DEVICE is a macro defined through Makefile, which is set to the value of the command line argument for flash.sh
}

void loop()
{
	device->loop();
}
