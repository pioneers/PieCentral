#ifndef LINE_FOLLOWER_H
#define LINE_FOLLOWER_H

#include "hibike_device.h"

#define NUM_PINS 3

uint8_t pins[NUM_PINS] = {IO0, IO1, IO2};


//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  LINE_FOLLOWER,  // Device Type
  0,              // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

// function prototypes
void setup();
void loop();


#endif /* LINE_FOLLOWER_H */
