#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"

#define NUM_PINS 3
#define IN_0 A0
#define IN_1 A1
#define IN_2 A2

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  POTENTIOMETER,                      // Device Type
  1,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

// function prototypes
void setup();
void loop();

uint8_t device_read(uint8_t param, uint8_t* data, size_t len);

#endif /* EX_DEVICE_H */
