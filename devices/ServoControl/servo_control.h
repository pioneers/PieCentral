#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"

#define NUM_PINS 4
#define IN_0 A0
#define IN_1 A1
#define IN_2 A2
#define IN_3 A3

#define LED_PIN 13
//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  SERVO_CONTROL,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////
char *DESCRIPTION = 
"{"
"    \"deviceID\": \"0x07\","
"    \"deviceName\": \"ServoControl\","
"    \"dataFormat\": {"
"        \"formatString\": \"\","
"        \"parameters\": []"
"    },"
"    \"params\": ["
"        \"dataUpdate\","
"        \"servo0\","
"        \"servo1\","
"        \"servo2\","
"        \"servo3\""
"    ]"
"}";
// function prototypes
void setup();
void loop();


#endif /* EX_DEVICE_H */