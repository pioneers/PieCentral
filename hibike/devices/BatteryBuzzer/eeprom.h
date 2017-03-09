#ifndef EEPROM_H
#define EEPROM_H

#include <EEPROM.h>
#include "battery_buzzer.h"

float get_calibration();

void update_triple_calibration();

void write_single_eeprom(float val);

void write_triple_eeprom(float val1, float val2, float val3);

void clear_eeprom();

#endif

