#ifndef RFID_H
#define RFID_H

#include "hibike_device.h"
 
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
