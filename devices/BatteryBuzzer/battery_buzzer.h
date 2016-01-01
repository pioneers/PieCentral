#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"

#define READ_ENABLE_PIN 9
#define BUZZER_PIN 10
#define BUZZER_FREQ 1000

#define CELL_0 A0
#define CELL_1 A1
#define CELL_2 A2
// units all voltages are recorded in
#define VREF 1023

// 3.5V
#define SAFE_THRESHOLD 716

// TBD
#define CONNECTED_THRESHOLD 100

// 1.0V
#define BALANCE_THRESHOLD 204

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  BATTERY_BUZZER,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

void read_voltage();

uint16_t abs_diff(uint16_t a, uint16_t b);

#define NUM_PARAMS 6


// function prototypes
void setup();
void loop();


#endif /* EX_DEVICE_H */