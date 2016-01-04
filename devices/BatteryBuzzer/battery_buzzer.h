#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"

#define READ_ENABLE_PIN 9
#define BUZZER_PIN 10
#define BUZZER_FREQ 1000

#define BATT_0 A0
#define BATT_1 A1
#define BATT_2 A2
#define NUM_CELLS 3
// units analogRead() uses
#define VOLTS_PER_UNIT (5.0/1023.0)

#define LOW_VOLTAGE_ENTER_THRESHOLD 3.5
#define LOW_VOLTAGE_EXIT_THRESHOLD 3.7

// connectivity is checked on raw values, not computed voltages
#define DISCONNECTED_ENTER_THRESHOLD 50
#define DISCONNECTED_EXIT_THRESHOLD 60

#define UNBALANCED_ENTER_THRESHOLD 1.0
#define UNBALANCED_EXIT_THRESHOLD 0.8

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  BATTERY_BUZZER,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////
///
typedef enum {
  CELL_SAFE,
  CELL_LOW_VOLTAGE,
  CELL_UNBALANCED,
  CELL_DISCONNECTED
} cell_state;

cell_state new_state();

void read_voltage();

float abs_diff(float a, float b);



// function prototypes
void setup();
void loop();


#endif /* EX_DEVICE_H */