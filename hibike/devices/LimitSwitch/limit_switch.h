#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  LIMIT_SWITCH,                      // Device Type
  0,                                 // Year
  UID_RANDOM,                        // ID
};
///////////////////////////////////////////////

#define NUM_SWITCHES 4
#define IN_0 A0
#define IN_1 A1
#define IN_2 A2
#define IN_3 A3

// function prototypes
void setup();
void loop();


#endif /* EX_DEVICE_H */