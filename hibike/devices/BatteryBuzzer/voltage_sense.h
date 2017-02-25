#ifndef VOLTAGE_SENSE_H
#define VOLTAGE_SENSE_H


#include "eeprom.h"
#include "battery_buzzer.h"
#include "disp_8.h"

void setup_sensing();

void measure_cells();

void handle_calibration();

float calibrate();

#endif