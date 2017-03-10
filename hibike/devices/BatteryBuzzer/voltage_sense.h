#ifndef VOLTAGE_SENSE_H
#define VOLTAGE_SENSE_H

#include "eeprom.h"
#include "battery_buzzer.h"
#include "disp_8.h"

extern float v_cell1;
extern float v_cell2;
extern float v_cell3;
extern float v_batt;
extern float dv_cell2;
extern float dv_cell3;
extern float vref_guess;

extern float calib[];

void setup_sensing();

void measure_cells();

void handle_calibration();

float calibrate();

#endif

