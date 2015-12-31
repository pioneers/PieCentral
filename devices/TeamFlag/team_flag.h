#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"

#define NUM_PARAMS 8

#define NUM_PINS 6
// Team LEDs
#define BLUE 6    // PWM
#define YELLOW 9  // PWM
// Status LEDs
#define STAT0 A0
#define STAT1 A1
#define STAT2 A2
#define STAT3 A3

#define LED_PIN 13
//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  TEAM_FLAG,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////
char *DESCRIPTION =         
"{"
"    \"deviceID\": \"0x05\","
"    \"deviceName\": \"TeamFlag\","
"    \"dataFormat\": {"
"        \"formatString\": \"\","
"        \"parameters\": []"
"    },"
"    \"params\": ["
"        \"dataUpdate\","
"        \"team\","
"        \"mode\","
"        \"blue\","
"        \"yellow\","
"        \"s1\","
"        \"s2\","
"        \"s3\","
"        \"s4\""
"    ]"
"}";

enum {
  MODE_INITIAL = 0,  // Initial mode
  MODE_DIRECT = 1,   // All LEDs controlled by the other parameters
  MODE_DEMO = 2,     // Everything blinking quickly
  MODE_ERROR = 3,    // Blink status LEDs quickly but leave team LEDs
};
enum {
  TEAM_BLUE = 0,
  TEAM_YELLOW = 1,
  TEAM_NONE = 255,
};

// function prototypes
void setup();
void loop();

// Parameter Update 
void update_param(uint8_t param, uint32_t value);

// Device Update
void deviceUpdate(uint8_t param, uint32_t value);
uint16_t setLed(uint8_t pin, uint16_t value);
void setupMode(uint8_t mode);
void modeUpdateLeds(uint8_t mode);

// functions to control this device
void toggleLED();

#endif /* EX_DEVICE_H */
