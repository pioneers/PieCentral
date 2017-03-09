#ifndef LINE_FOLLOWER_H
#define LINE_FOLLOWER_H

#include "hibike_device.h"

#define NUM_PINS 3

uint8_t pins[NUM_PINS] = {A0, A1, A2};


//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  LINE_FOLLOWER,  // Device Type
  1,              // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

// function prototypes
void setup();
void loop();
uint8_t device_read(uint8_t param, uint8_t* data, size_t len);

#endif /* LINE_FOLLOWER_H */
