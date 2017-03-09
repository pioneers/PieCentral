#ifndef BATTERY_BUZZER_H
#define BATTERY_BUZZER_H

#include "hibike_device.h"
#include "eeprom.h"
#include "safety.h"
#include "voltage_sense.h"
#include "disp_8.h"

extern bool triple_calibration;
extern int buzzer;

typedef enum {
  IS_UNSAFE,
  CALIBRATED,
  V_CELL1,
  V_CELL2,
  V_CELL3,
  V_BATT,
  DV_CELL2,
  DV_CELL3
} PARAMS;

// function prototypes
void setup();
void loop();

uint32_t device_write(uint8_t param, uint8_t* data, size_t len);
uint8_t device_read(uint8_t param, uint8_t* data, size_t len);
#endif /* EX_DEVICE_H */

