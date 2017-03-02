#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"

#define NUM_PARAMS 8

#define NUM_PINS 6
// Team LEDs
#define BLUE 7    // PWM
#define YELLOW 8  // PWM
// Status LEDs
#define LED1 A3
#define LED2 A2
#define LED3 A1
#define LED4 A0

#define LED_PIN 13

// PARAM 0 will be mode, to be implemented later
#define PARAM_BLUE 1
#define PARAM_YELLOW 2

#define PARAM_LED1 3
#define PARAM_LED2 4
#define PARAM_LED3 5
#define PARAM_LED4 6

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  TEAM_FLAG,                      // Device Type
  1,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

// function prototypes
void setup();
void loop();

uint8_t device_read(uint8_t param, uint8_t* data, size_t len);
uint32_t device_write(uint8_t param, uint8_t* data, size_t len);


// functions to control this device
void toggleLED();
void setLed(uint8_t pin, uint16_t value);
uint8_t getLed(uint8_t pin);

#endif /* EX_DEVICE_H */
