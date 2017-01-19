#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  EXAMPLE_DEVICE,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

#define NUM_PARAMS 6 //change to however many params are needed

typedef enum {
  VALUE_0 = 0,
  VALUE_1 = 1,
  VALUE_2 = 2,
  VALUE_3 = 3,
  VALUE_4 = 4,
  VALUE_5 = 5
} param;

// function prototypes
void setup();
void loop();

#endif /* EX_DEVICE_H */
