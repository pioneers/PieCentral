#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"
#include <Servo.h>

#define NUM_PINS 2
#define SERVO_0 5
#define SERVO_1 6

#define LED_PIN 13 //unchanged
//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  SERVO_CONTROL,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

typedef enum {
  SERVOPARAM0,
  SERVOPARAM1,
  TOGGLE0,
  TOGGLE1,
} param;

// function prototypes
void setup();
void loop();

// Helper functions
uint32_t toggle_servo(int servo_num, uint32_t toggle);

#endif /* EX_DEVICE_H */
