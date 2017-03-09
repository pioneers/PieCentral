#ifndef BATTERY_BUZZER_H
#define BATTERY_BUZZER_H

#include "hibike_device.h"
#include "eeprom.h"
#include "safety.h"
#include "voltage_sense.h"
#include "disp_8.h"

extern bool triple_calibration;
extern int buzzer;


// function prototypes
void setup();
void loop();

uint32_t device_write(uint8_t param, uint8_t* data, size_t len);
uint8_t device_read(uint8_t param, uint8_t* data, size_t len);
#endif /* EX_DEVICE_H */

