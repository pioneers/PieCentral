#ifndef BATTERY_BUZZER_H
#define BATTERY_BUZZER_H

#include "hibike_device.h"
#include "eeprom.h" //implement
#include "safety.h" //implement
#include "voltage_sense.h"
#include "disp_8.h"


extern float v_cell1;
extern float v_cell2;
extern float v_cell3;
extern float v_batt;
extern float dv_cell2;
extern float dv_cell3;
extern float vref_guess;
extern bool prints;

extern bool calibrated;
extern float calib[];
extern bool triple_calibration;
extern int buzzer;

extern unsigned long last_print_time;

// extern bool unsafe_status


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

uint32_t device_write(uint8_t param, uint8_t* data, size_t len);
uint8_t device_read(uint8_t param, uint8_t* data, size_t len);
#endif /* EX_DEVICE_H */
