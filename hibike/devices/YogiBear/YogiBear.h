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
  DUTY,
  FAULT, //EN Value. high = operating, low = fault
  FORWARD,
  REVERSE
} param;

// function prototypes
void setup();
void loop();


#endif /* YOGI_BEAR_FOLLOWER_H */