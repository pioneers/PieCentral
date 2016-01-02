#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_message.h"
#include "devices.h"
#include <Servo.h>

#define NUM_PARAMS 5

#define NUM_PINS 4
#define SERVO_0 6
#define SERVO_1 9
#define SERVO_2 10
#define SERVO_3 11

#define LED_PIN 13

// function prototypes
void setup();
void loop();

// Parameter Update 
void update_param(uint8_t param, uint32_t value);

// functions to control this device
void toggleLED();

#endif /* EX_DEVICE_H */
