#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"


//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  0xFFFF,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////




#define NUM_PARAMS 6

#define LED_PIN 13

//extern hibike_uid_t UID;
// function prototypes
void setup();
void loop();


#endif /* EX_DEVICE_H */