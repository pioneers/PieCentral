#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"
#include <Servo.h>

#define NUM_PINS 4
#define SERVO_0 6
#define SERVO_1 9
#define SERVO_2 10
#define SERVO_3 11

#define LED_PIN 13
//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  SERVO_CONTROL,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

// function prototypes
void setup();
void loop();


#endif /* EX_DEVICE_H */
