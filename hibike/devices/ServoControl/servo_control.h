#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"
#include <Servo.h>

#define NUM_PINS 2
#define SERVO_0 5
#define SERVO_1 6

#define LED_PIN 13

#define SERVO_RANGE 1000
#define SERVO_CENTER 1500
//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  SERVO_CONTROL,                      // Device Type
  1,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

// function prototypes
void setup();
void loop();
void disableAll();

#endif /* EX_DEVICE_H */
