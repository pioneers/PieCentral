#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"
 
// You must replace EXAMPLE_DEVICE with the device id of the device you are writing firmware for
// The device id's are defined in hibike/lib/hibike/devices.h
// The device id should correspond to a device id in hibike/hibikeDevices.json

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  RFID,                      // Device Type
  1,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

// this is an optional device specific enum to make implementation easier
typedef enum {
  ID = 0,
  TAG_DETECT = 1,
} Param;

// function prototypes
void setup();
void loop();

#endif /* RFID_H */
