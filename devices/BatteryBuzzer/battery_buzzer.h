#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"

#define READ_ENABLE_PIN 9
#define BUZZER_PIN 10
#define BUZZER_FREQ 1000

#define BATT_0 A0
#define BATT_1 A1
#define BATT_2 A2

// units analogRead() uses
#define VOLTS_PER_UNIT (5.0/1023.0)

// 3.5V
#define SAFE_THRESHOLD 3.5

// connectivity is checked on raw values, not computed voltages
#define CONNECTED_THRESHOLD 50

// 1.0V
#define BALANCE_THRESHOLD 1.0

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  BATTERY_BUZZER,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

void read_voltage();

float abs_diff(float a, float b);



// function prototypes
void setup();
void loop();


#endif /* EX_DEVICE_H */