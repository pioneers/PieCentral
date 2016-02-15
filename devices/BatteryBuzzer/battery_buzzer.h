#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"
#include "pitches.h"

#define READ_ENABLE_PIN 9
#define BUZZER_PIN 10
#define BUZZER_LED_PIN 11
#define BUZZER_FREQ NOTE_A4
#define BUZZER_DISCONNECT_FREQ NOTE_A3
#define BUZZER_BROKEN_FREQ NOTE_DS2

#define NUM_CELLS 3
#define BATT_0 A0
#define BATT_1 A1
#define BATT_2 A2
#define BATT_0_SCALE 2.0  // From voltage divider
#define BATT_1_SCALE 4.0
#define BATT_2_SCALE 6.1
#define BATT_INPUT {A0, A1, A2}
#define BATT_CHANNELS {7, 6, 5}  // The ADC channels for A0, A1, A2 on atmega32u4
#define NUM_SAMPLES 62  // Average this many readings per cell voltage, should not be greater than 63
// units analogRead() uses
#define UNITS_PER_VOLT (5.0/1023.0)  // From ADC
#define PRESCALE (1/(NUM_SAMPLES*UNITS_PER_VOLT))
#define DEFAULT_CALIBRATION {PRESCALE*BATT_0_SCALE, PRESCALE*BATT_1_SCALE, PRESCALE*BATT_2_SCALE}
#define BLINK_AFTER_MEASURE 10  // At 2Hz

// Calibration reference (from external voltage source)
#define MIN_REF_VOLT 4.5
#define MAX_REF_VOLT 5.5
#define REF_VOLT 5

#define LOW_VOLTAGE_ENTER_THRESHOLD 3.4
#define LOW_VOLTAGE_EXIT_THRESHOLD 3.8

#define UNBALANCED_ENTER_THRESHOLD 0.6
#define UNBALANCED_EXIT_THRESHOLD 0.2

// connectivity is checked on raw values, not computed voltages
#define DISCONNECTED_THRESHOLD 100  // (~0.5 Volts)
#define DISCONNECTED_COUNT 10

#define MEASURE_DELAY_UNSAFE_MS 1000

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

// function prototypes
void setup();
void loop();

void calibrationSetup(bool beep);
void readTimerStart();
void updateSafety();
void updateCellStates();

cell_state new_state(float voltage, float nextCellVoltage, bool disconnected, cell_state lastState);
float abs_diff(float a, float b);

#endif /* EX_DEVICE_H */
