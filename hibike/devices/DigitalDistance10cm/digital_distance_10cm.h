#ifndef DIGITAL_DISTANCE_10CM_H
#define DIGITAL_DISTANCE_10CM_H

#include "hibike_device.h"

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  DIGITAL_DISTANCE_10CM,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////



#define NUM_PARAMS 1


// function prototypes
void setup();
void loop();


#endif /* DIGITAL_DISTANCE_10CM_H* */
