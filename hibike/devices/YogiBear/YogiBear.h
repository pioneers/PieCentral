#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  YOGI_BEAR,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////



#define NUM_PARAMS 5

typedef enum {
  DUTY = 0,
  FAULT = 1,
  FORWARD = 2,
  REVERSE = 3
} param;

#define PARAM_DUTY 0
#define PARAM_FORWARD 1

// function prototypes
void setup();
void loop();


#endif /* EX_DEVICE_H */
