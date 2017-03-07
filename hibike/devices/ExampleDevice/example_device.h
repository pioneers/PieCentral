#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"
 
// You must replace EXAMPLE_DEVICE with the device id of the device you are writing firmware for
// The device id's are defined in hibike/lib/hibike/devices.h
// The device id should correspond to a device id in hibike/hibikeDevices.json

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  EXAMPLE_DEVICE,                      // Device Type
  1,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

// this is an optional device specific enum to make implementation easier
// The value of each parameter should match the number defined in the jason file.
typedef enum {
	KUMIKO = 0,
	HAZUKI = 1,
	SAPPHIRE = 2,
	REINA = 3,
	ASUKA = 4,
	HARUKA = 5,
	KAORI = 6,
	NATSUKI = 7,
	YUKO = 8,
	MIZORE = 9,
	NOZOMI = 10,
	SHUICHI = 11,
	TAKUYA = 12,
	RIKO = 13,
	AOI = 14,
	NOBORU = 15
} ExampleDeviceParam;

// function prototypes
void setup();
void loop();

#endif /* EX_DEVICE_H */
