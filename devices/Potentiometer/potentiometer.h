#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"

#define NUM_PARAMS 5

#define NUM_PINS 4
#define IN_0 A0
#define IN_1 A1
#define IN_2 A2
#define IN_3 A3

#define LED_PIN 13
//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  POTENTIOMETER,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

// function prototypes
void setup();
void loop();


#endif /* EX_DEVICE_H */