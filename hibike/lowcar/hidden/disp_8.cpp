//code that deals with displaying the data to the outside world.
#include "disp_8.h"

disp_8::disp_8 (VoltageTracker v_tracker)
{

  this->digitPins[0] = DISP_PIN_1;
  this->digitPins[1] = DISP_PIN_2;
  this->digitPins[2] = DISP_PIN_3;
  this->digitPins[3] = DISP_PIN_4;

  this->last_LED_time = 0;  //Time the last LED switched
  this->sequence = 0; //used to switch states for the display.  Remember that the hangle_8_segment cannot be blocking.

  this->segment_8_run = NORMAL_VOLT_READ;  //0 for the normal voltage readout.  1 for "Clear Calibration".  2 for "New Calibration"

  this->voltage_tracker = v_tracker;
}



void disp_8::setup_display()
{
  disp.setDigitPins(numOfDigits, digitPins);
  disp.setDPPin(DECIMAL_POINT);  //set the Decimal Point pin to #1
}


void disp_8::test_display() //a function to ensure that all outputs of the display are working.
//On the current PDB, this should display "8.8.8.8."  The library is capable of handling : and ', but the wires are not hooked up to it.
{
  for(int i = 0; i<250; i++)
  {
    disp.write("8.8.8.8."); //this function call takes a surprising amount of time, probably because of how many characters are in it.
  }
  disp.clearDisp();
}


void disp_8::handle_8_segment() //handles the 8-segment display, and prints out the global values.
//MUST be called in the loop() without any if's
{
  if(segment_8_run == NORMAL_VOLT_READ)
  {
    //Shows text / numbers of all voltages & then individual cells.
    //Changed every Second
    switch(sequence) {
      case 0: disp.write("ALL");
              break;
      case 1: disp.write(voltage_tracker.get_voltage(V_BATT), 2);
              break;
      case 2: disp.write("CEL.1");
              break;
      case 3: disp.write(voltage_tracker.get_voltage(V_CELL1), 2);
              break;
      case 4: disp.write("CEL.2");
              break;
      case 5: disp.write(voltage_tracker.get_voltage(DV_CELL2), 2);
              break;
      case 6: disp.write("CEL.3");
              break;
      case 7: disp.write(voltage_tracker.get_voltage(DV_CELL3), 2);
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
    if(voltage_tracker.get_triple_calibration())
    {
      switch(sequence) {
        case 0: disp.write("CAL");
                break;
        case 1: disp.write("DONE");
                break;
        case 2: disp.write("CAL.1");
                break;
        case 3: disp.write(voltage_tracker.get_calib(0), 3);
                break;
        case 4: disp.write("CAL.2");
                break;
        case 5: disp.write(voltage_tracker.get_calib(1), 3);
                break;
        case 6: disp.write("CAL.3");
                break;
        case 7: disp.write(voltage_tracker.get_calib(2), 3);
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
        case 3: disp.write(voltage_tracker.get_voltage(VREF_GUESS), 3);
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

void disp_8::start_8_seg_sequence(SEQ_NUM sequence_num)
{
  segment_8_run = sequence_num; //rel the display to run the right sequence
  sequence = 0;  //and reset the step in the sequence to zero.
  last_LED_time = millis();
}
