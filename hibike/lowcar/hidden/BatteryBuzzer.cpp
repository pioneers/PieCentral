#include "BatteryBuzzer.h"
#include "pdb_defs.h"

// default constructor simply specifies DeviceID and and year to generic constructor
// initalizes helper class objects and pre-existing variables
BatteryBuzzer::BatteryBuzzer () :
  Device (DeviceID:: BATTERY_BUZZER, 1),
  bb_voltage_tracker (VoltageTracker()),
  bb_eeprom (eeprom(bb_voltage_tracker)),
  bb_disp_8 (disp_8(bb_voltage_tracker)),
  bb_safety (safety(bb_voltage_tracker, buzzer)),
  bb_voltage_sense (voltage_sense(bb_eeprom, bb_disp_8, bb_voltage_tracker))
{
  this->buzzer = 10;
  this->last_check_time = 0; //for loop counter

  this->calibrated = false;

  bb_voltage_tracker.set_voltage(VREF_GUESS, ADC_REF_NOM); //initial guesses, based on datasheet
  bb_voltage_tracker.set_calib(0, ADC_REF_NOM);
  bb_voltage_tracker.set_calib(1, ADC_REF_NOM);
  bb_voltage_tracker.set_calib(2, ADC_REF_NOM);
}

uint8_t BatteryBuzzer::device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len)
{
  if (data_buf_len > sizeof(bool)) {
    if (param == IS_UNSAFE) {
      data_buf[0] = bb_safety.is_unsafe();
      return sizeof(bool);
    }
    if (param == CALIBRATED) {
      data_buf[1] = is_calibrated();
      return sizeof(bool);
    }
  }

  if (data_buf_len < sizeof(float) || param >= 8) {
    return 0;
  }

  float *float_buf = (float*) data_buf;

  switch(param) {
      case V_CELL1:
        float_buf[0] = bb_voltage_tracker.get_voltage(V_CELL1);
        break;
      case V_CELL2:
        float_buf[0] = bb_voltage_tracker.get_voltage(V_CELL2);
        break;
      case V_CELL3:
        float_buf[0] = bb_voltage_tracker.get_voltage(V_CELL3);
        break;
      case V_BATT:
        float_buf[0] = bb_voltage_tracker.get_voltage(V_BATT);
        break;
      case DV_CELL2:
        float_buf[0] = bb_voltage_tracker.get_voltage(DV_CELL2);
        break;
      case DV_CELL3:
        float_buf[0] = bb_voltage_tracker.get_voltage(DV_CELL3);
        break;
    }

    data_buf = (uint8_t*) float_buf;
    return sizeof(float);

}

void BatteryBuzzer::device_enable ()
{
  pinMode(buzzer, OUTPUT);

  bb_disp_8.setup_display();
  bb_disp_8.test_display(); //For production to check that the LED display is working
  bb_voltage_sense.setup_sensing();
}

void BatteryBuzzer::device_actions ()
{
  bb_disp_8.handle_8_segment();
  bb_voltage_sense.handle_calibration();

  if ((millis() - last_check_time) > 250) {
    bb_voltage_sense.measure_cells();
    last_check_time = millis();
    bb_safety.handle_safety();
  }
}

bool BatteryBuzzer::is_calibrated ()
{
  //triple calibration arrays are all default values
  float calib_0 = bb_voltage_tracker.get_calib(0);
  float calib_1 = bb_voltage_tracker.get_calib(1);
  float calib_2 = bb_voltage_tracker.get_calib(2);
  if (bb_voltage_tracker.get_triple_calibration() && (calib_0 == ADC_REF_NOM) && (calib_1 == ADC_REF_NOM) && (calib_2 == ADC_REF_NOM)) {
    return false;
  }
  //calibration value is set to default
  if (!bb_voltage_tracker.get_triple_calibration() && (bb_eeprom.get_calibration() == -1.0)) {
    return false;
  }
  //device is calibrated: no default values
  return true;
}
