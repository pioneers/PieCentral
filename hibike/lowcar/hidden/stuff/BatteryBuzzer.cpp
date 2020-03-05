#include "BatteryBuzzer.h"
#include "pdb_defs.h"

// default constructor simply specifies DeviceID and and year to generic constructor
// initalizes helper class objects and pre-existing variables
BatteryBuzzer::BatteryBuzzer () :
  Device (DeviceID:: BATTERY_BUZZER, 1),
  bb_voltage_tracker (VoltageTracker()),
  bb_eeprom (eeprom(bb_voltage_tracker)),
  //bb_disp_8 (disp_8(bb_voltage_tracker))
  bb_safety (safety(bb_voltage_tracker, buzzer)),
  disp(SevenSeg(A, B, C, D, E, G, H)),
  bb_voltage_sense (voltage_sense(bb_eeprom, bb_voltage_tracker))
{
  this->buzzer = 10;
  this->last_check_time = 0; //for loop counter

  //SevenSeg disp(A, B, C, D, E, G, H);

  //this->calibrated = false;

  this->digitPins[0] = DISP_PIN_1;
  this->digitPins[1] = DISP_PIN_2;
  this->digitPins[2] = DISP_PIN_3;
  this->digitPins[3] = DISP_PIN_4;

  this->last_LED_time = 0;  //Time the last LED switched
  this->sequence = 0; //used to switch states for the display.  Remember that the hangle_8_segment cannot be blocking.

  this->segment_8_run = NORMAL_VOLT_READ;  //0 for the normal voltage readout.  1 for "Clear Calibration".  2 for "New Calibration"
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

  bb_voltage_tracker.set_voltage(VREF_GUESS, ADC_REF_NOM); //initial guesses, based on datasheet
  bb_voltage_tracker.set_calib(0, ADC_REF_NOM);
  bb_voltage_tracker.set_calib(1, ADC_REF_NOM);
  bb_voltage_tracker.set_calib(2, ADC_REF_NOM);

  setup_display();
  disp.clearDisp();
  test_display(); //For production to check that the LED display is working
  bb_voltage_sense.setup_sensing();
}

void BatteryBuzzer::device_actions ()
{
  setup_display();
  disp.clearDisp();
 
  handle_8_segment();
  SEQ_NUM mode = bb_voltage_sense.handle_calibration();
  bb_voltage_sense.setup_sensing(); 
  //start_8_seg_sequence(0);

  if ((millis() - last_check_time) > 250) {
    bb_voltage_sense.measure_cells();
    last_check_time = millis();
    bb_safety.handle_safety();
  }
  disp.clearDisp();
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

void BatteryBuzzer::setup_display()
{
  disp.setDigitPins(numOfDigits, digitPins);
  disp.setDPPin(DECIMAL_POINT);  //set the Decimal Point pin to #1
}


void BatteryBuzzer::test_display() //a function to ensure that all outputs of the display are working.
//On the current PDB, this should display "8.8.8.8."  The library is capable of handling : and ', but the wires are not hooked up to it.
{
  for(int i = 0; i<250; i++)
  {
    disp.write("8.8.8.8."); //this function call takes a surprising amount of time, probably because of how many characters are in it.
  }
  disp.clearDisp();
}


void BatteryBuzzer::handle_8_segment() //handles the 8-segment display, and prints out the global values.
//MUST be called in the loop() without any if's
{
  if(segment_8_run == NORMAL_VOLT_READ)
  {
    //Shows text / numbers of all voltages & then individual cells.
    //Changed every Second
    switch(sequence) {
      case 0: disp.write("ALL");
              break;
      case 1: disp.write(bb_voltage_tracker.get_voltage(V_BATT), 2);
              break;
      case 2: disp.write("CEL.1");
              break;
      case 3: disp.write(bb_voltage_tracker.get_voltage(V_CELL1), 2);
              break;
      case 4: disp.write("CEL.2");
              break;
      case 5: disp.write(bb_voltage_tracker.get_voltage(DV_CELL2), 2);
              break;
      case 6: disp.write("CEL.3");
              break;
      case 7: disp.write(bb_voltage_tracker.get_voltage(DV_CELL3), 2);
              break;
    }

    if (millis() > (last_LED_time + 1000)) //every second
    {
      sequence = sequence + 1;
      if(sequence == 8)
      {
        sequence = 0;
      }
      last_LED_time = millis();
    }
  }
  else if(segment_8_run == CLEAR_CALIB)
  {
    if(sequence == 0)
    {
      disp.write("CAL");
    }
    else if(sequence == 1)
    {
      disp.write("CLR");
    }

    if (millis() > (last_LED_time + 750) ) //every 3/4 second
    {
      sequence = sequence + 1;
      if(sequence == 2)
      {
        start_8_seg_sequence(NORMAL_VOLT_READ); //return to default Programming... showing battery voltages.
      }
      last_LED_time = millis();
    }

  }
  else if(segment_8_run == NEW_CALIB)
  {
    if(bb_voltage_tracker.get_triple_calibration())
    {
      switch(sequence) {
        case 0: disp.write("CAL");
                break;
        case 1: disp.write("DONE");
                break;
        case 2: disp.write("CAL.1");
                break;
        case 3: disp.write(bb_voltage_tracker.get_calib(0), 3);
                break;
        case 4: disp.write("CAL.2");
                break;
        case 5: disp.write(bb_voltage_tracker.get_calib(1), 3);
                break;
        case 6: disp.write("CAL.3");
                break;
        case 7: disp.write(bb_voltage_tracker.get_calib(2), 3);
                break;
      }

      if (millis() > (last_LED_time + 750) ) //every 3/4 second
      {
        sequence = sequence + 1;
        if(sequence == 8)
        {
          start_8_seg_sequence(NORMAL_VOLT_READ); //return to default Programming... showing battery voltages.
        }
        last_LED_time = millis();
      }

    }
    else
    {
      switch(sequence) {
        case 0: disp.write("CAL");
                break;
        case 1: disp.write("DONE");
                break;
        case 2: disp.write("CAL");
                break;
        case 3: disp.write(bb_voltage_tracker.get_voltage(VREF_GUESS), 3);
                break;
      }

      if (millis() > (last_LED_time + 750) ) //every 3/4 second
      {
        sequence = sequence + 1;
        if(sequence == 4)
        {
          start_8_seg_sequence(NORMAL_VOLT_READ); //return to default Programming... showing battery voltages.
        }
        last_LED_time = millis();
      }
    }
  }
}

void BatteryBuzzer::start_8_seg_sequence(SEQ_NUM sequence_num)
{
  segment_8_run = sequence_num; //rel the display to run the right sequence
  sequence = 0;  //and reset the step in the sequence to zero.
  last_LED_time = millis();
}
