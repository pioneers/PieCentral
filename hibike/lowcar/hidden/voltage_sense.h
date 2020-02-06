#ifndef VOLTAGE_SENSE_H
#define VOLTAGE_SENSE_H

#include "eeprom.h"
#include "disp_8.h"
#include "VoltageTracker.h"

class voltage_sense
{
public:
  voltage_sense (eeprom ee_prom, disp_8 display_8, VoltageTracker v_tracker);

  void setup_sensing();

  void measure_cells();

  void handle_calibration();

  float calibrate();

private:
  VoltageTracker sense_voltage_tracker;
  eeprom sense_eeprom;
  disp_8 sense_disp_8;
};

#endif
