#ifndef EX_DEVICE_H
#define EX_DEVICE_H
#include "hibike_message.h"
#include "devices.h"

#define IN_PIN 10
#define LED_PIN 13

#define NUM_PARAMS 1
typedef enum {
  TEST_PARAM      = 0x00,
}param_index;

// function prototypes
void setup();
void loop();

// Parameter Update 
void update_param(uint8_t param, uint32_t value);

// functions to control this device
void toggleLED();

#endif /* EX_DEVICE_H */