#ifndef VOLTAGE_TRACKER_H
#define VOLTAGE_TRACKER_H

#include "pdb_defs.h"
#include <stdint.h>

class VoltageTracker
{
public:

  float get_voltage (uint8_t param);
  void set_voltage (uint8_t param, float value);

  float get_calib (uint8_t index);
  void set_calib (uint8_t index, float value);

  bool get_triple_calibration();
  void set_triple_calibration(bool triple_cal);


private:
  float v_cell1_var;  // param 3
  float v_cell2_var;  // param 4
  float v_cell3_var;  // param 5
  float v_batt_var;   // param 6
  float dv_cell2_var; // param 7
  float dv_cell3_var; // param 8
  float vref_guess_var; // param 9

  float* calib;

  bool triple_calibration;
};

#endif
