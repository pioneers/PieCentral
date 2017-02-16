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
typedef enum {
  VALUE_0 = 1,
  VALUE_1 = 11,
  VALUE_2 = 12,
  VALUE_3 = 13,
  VALUE_4 = 14,
  VALUE_5 = 7
} ExampleDeviceParam;

// function prototypes
void setup();
void loop();

#endif /* EX_DEVICE_H */
