#ifndef BATTERY_BUZZER_H
#define BATTERY_BUZZER_H

#include "Device.h"
#include "VoltageTracker.h"
//#include "disp_8.h"
#include "voltage_sense.h"
#include "eeprom.h"
#include "safety.h"
#include "pdb_defs.h"
#include <SevenSeg.h>
#include <Arduino.h>

const int numOfDigits = 4;

class BatteryBuzzer : public Device
{
public:
  bool triple_calibration;
  int buzzer;
  VoltageTracker bb_voltage_tracker;
  //disp_8 bb_disp_8;
  voltage_sense bb_voltage_sense;
  eeprom bb_eeprom;
  safety bb_safety;

  //constructs a BatteryBuzzer; simply calls generic Device constructor with device type and year
  BatteryBuzzer ();

  //overriden functions from Device class; see descriptions in Device.h
  virtual uint8_t device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len);
  virtual void device_enable ();
  virtual void device_actions ();

private:
  unsigned long last_check_time;
  //bool calibrated;

  SevenSeg disp;

  int digitPins[numOfDigits];
  unsigned long last_LED_time;  //Time the last LED switched
  int sequence; //used to switch states for the display.  Remember that the handle_8_segment cannot be blocking.

  SEQ_NUM segment_8_run;  //0 for the normal voltage readout.  1 for "Clear Calibration".  2 for "New Calibration"

  bool is_calibrated ();

  void start_8_seg_sequence(SEQ_NUM sequence_num);
  void handle_8_segment();
  void test_display();
  void setup_display();
};

#endif
