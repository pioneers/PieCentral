#ifndef BATTERY_BUZZER_H
#define BATTERY_BUZZER_H

#include "Device.h"
#include "VoltageTracker.h"
#include "disp_8.h"
#include "voltage_sense.h"
#include "eeprom.h"
#include "safety.h"

class BatteryBuzzer : public Device
{
public:
  bool triple_calibration;
  int buzzer;
  VoltageTracker voltage_tracker;
  disp_8 disp_8;
  voltage_sense voltage_sense;
  eeprom eeprom;
  safety safety;

  //constructs a BatteryBuzzer; simply calls generic Device constructor with device type and year
  BatteryBuzzer ();

  //overriden functions from Device class; see descriptions in Device.h
  virtual uint8_t device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len);
  virtual void device_enable ();
  virtual void device_actions ();

private:
  unsigned long last_check_time;
  bool calibrated;

  bool is_calibrated ();
};

#endif
