#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_message.h"
#include "Servo.h"

#define NUM_PARAMS 5

#define IN_PIN 14
#define LED_PIN 13

// function prototypes
void setup();
void loop();

// Parameter Update 
void update_param(uint8_t param, uint32_t value);

// functions to control this device
void toggleLED();

#endif /* EX_DEVICE_H */