#include "BatteryBuzzer.h"
#include "pdb_defs.h"

// default constructor simply specifies DeviceID and and year to generic constructor
// initalizes helper class objects and pre-existing variables
BatteryBuzzer::BatteryBuzzer () : Device (DeviceID:: BATTERY_BUZZER, 1)
{
  int BatteryBuzzer::buzzer = 10;
  unsigned long BatteryBuzzer::last_check_time = 0; //for loop counter

  bool BatteryBuzzer::calibrated = false;

  VoltageTracker BatteryBuzzer::voltage_tracker = VoltageTracker ();
  eeprom BatteryBuzzer::eeprom = eeprom (BatteryBuzzer::voltage_tracker);
  disp_8 BatteryBuzzer::disp_8 = disp_8 (BatteryBuzzer::voltage_tracker);
  safety BatteryBuzzer::safety = safety (BatteryBuzzer::voltage_tracker, BatteryBuzzer::buzzer);
  voltage_sense BatteryBuzzer::voltage_sense = voltage_sense (BatteryBuzzer::eeprom, BatteryBuzzer::disp_8, BatteryBuzzer::voltage_tracker);

  BatteryBuzzer::voltage_tracker.set(VREF_GUESS, ADC_REF_NOM); //initial guesses, based on datasheet
  BatteryBuzzer::voltage_tracker.set_calib(0, ADC_REF_NOM);
  BatteryBuzzer::voltage_tracker.set_calib(1, ADC_REF_NOM);
  BatteryBuzzer::voltage_tracker.set_calib(2, ADC_REF_NOM);
}

uint8_t BatteryBuzzer::device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len)
{
  if (data_buf_len > sizeof(bool)) {
    if (param == IS_UNSAFE) {
      data_buf[0] = BatteryBuzzer::safety.is_unsafe();
      return sizeof(bool);
    }
    if (param == CALIBRATED) {
      data_buf[1] = BatteryBuzzer::is_calibrated();
      return sizeof(bool);
    }
  }

  if (data_buf_len < sizeof(float) || param >= 8) {
    return 0;
  }

  float *float_buf = (float*) data_buf;

  switch(param) {
      case V_CELL1:
        float_buf[0] = BatteryBuzzer::voltage_tracker.get(V_CELL1);
        break;
      case V_CELL2:
        float_buf[0] = BatteryBuzzer::voltage_tracker.get(V_CELL2);
        break;
      case V_CELL3:
        float_buf[0] = BatteryBuzzer::voltage_tracker.get(V_CELL3);
        break;
      case V_BATT:
        float_buf[0] = BatteryBuzzer::voltage_tracker.get(V_BATT);
        break;
      case DV_CELL2:
        float_buf[0] = BatteryBuzzer::voltage_tracker.get(DV_CELL2);
        break;
      case DV_CELL3:
        float_buf[0] = BatteryBuzzer::voltage_tracker.get(DV_CELL3);
        break;
    }

    data_buf = (uint8_t*) float_buf;
    return sizeof(float);

}

void BatteryBuzer::device_enable ()
{
  pinMode(BatteryBuzzer::buzzer, OUTPUT);

  BatteryBuzzer::disp_8.setup_display();
  BatteryBuzzer::disp_8.test_display(); //For production to check that the LED display is working
  BatteryBuzzer::voltage_sense.setup_sensing();
}

uint8_t BatteryBuzzer::device_actions ()
{
  BatteryBuzzer::disp_8.handle_8_segment();
  BatteryBuzzer::disp_8.handle_8_calibration();

  if ((millis() - last_check_time) > 250) {
    BatteryBuzzer::voltage_sense.measure_cells();
    BatteryBuzzer::last_check_time = millis();
    BatteryBuzzer::safety.handle_safety();
  }
}

bool BatteryBuzzer::is_calibrated ()
{
  //triple calibration arrays are all default values
  float calib_0 = BatteryBuzzer::voltage_tracker.get_calib(0)
  float calib_1 = BatteryBuzzer::voltage_tracker.get_calib(1)
  float calib_2 = BatteryBuzzer::voltage_tracker.get_calib(2)
  if (BatteryBuzzer::voltage_tracker.get_triple_calibration() && (calib_0 == ADC_REF_NOM) && (calib_1 == ADC_REF_NOM) && (calib_2 == ADC_REF_NOM)) {
    return false;
  }
  //calibration value is set to default
  if (!BatteryBuzzer::voltage_tracker.get_triple_calibration() && (BatteryBuzzer::eeprom.get_calibration() == -1.0)) {
    return false;
  }
  //device is calibrated: no default values
  return true;
}
