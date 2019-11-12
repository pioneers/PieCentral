/*
 * This is the actual Arduino sketch that acts as the "main" for the device.
 * It is supposed to be kept as simple as possible.
 */

#include "Device.h"

Device *device; //declare this device

void setup()
{
	//TODO: put actual params here once we've written the Device class
	//TODO: should actually be like new LimitSwitch() or new PolarBear() or something like that
	device = new Device();
}

void loop()
{
	device->loop();
}