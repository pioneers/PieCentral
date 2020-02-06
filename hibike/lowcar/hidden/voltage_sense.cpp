#include "voltage_sense.h"
#include "disp_8.h"
#include "pdb_defs.h"

// Utility class that deals with calibration and measuring cell voltages.

voltage_sense::voltage_sense (eeprom ee_prom, disp_8 display_8, VoltageTracker v_tracker)
{
  eeprom eeprom = ee_prom;
  disp_8 disp_8 = display_8;
  VoltageTracker voltage_tracker = v_tracker;
}

void voltage_sense::setup_sensing()
{
  pinMode(ENABLE, OUTPUT);
  pinMode(CALIB_BUTTON, INPUT);

  //for stable (if unknown) internal voltage.
  analogReference(INTERNAL);

  //let's turn enable on, so we can measure the battery voltage.
  digitalWrite(ENABLE, HIGH);

  if(voltage_tracker.get_triple_calibration())
  {
    eeprom.update_triple_calibration();  //and then update the calibration values I use based on what I now know
  }
  else
  {
    float val = eeprom.get_calibration();
    if(val > 0) //by convention, val is -1 if there's no calibration.
    {
      voltage_tracker.set_voltage(VREF_GUESS, val);
    }
  }
}


void voltage_sense::measure_cells() //measures the battery cells. Should call at least twice a second, but preferrably 5x a second.  No use faster.
{
    int r_cell1 = analogRead(CELL1);
    int r_cell2 = analogRead(CELL2);
    int r_cell3 = analogRead(CELL3);

    float calib_0 = voltage_tracker.get_calib(0);
    float calib_1 = voltage_tracker.get_calib(1);

    float new_v_cell1 = float(r_cell1) * (R2 + R5) / R5 * calib_0 / ADC_COUNTS;
    float new_v_cell2 = float(r_cell2) * (R3 + R6) / R6 * calib_1 / ADC_COUNTS;
    float new_v_cell3 =(R4 +  R7) / R7 * calib[2] / ADC_COUNTS;

    voltage_tracker.set_voltage(V_CELL1, new_v_cell1);
    voltage_tracker.set_voltage(V_CELL2, new_v_cell2);
    voltage_tracker.set_voltage(V_CELL3, new_v_cell3);

    voltage_tracker.set_voltage(DV_CELL2, new_v_cell2 - new_v_cell1);
    voltage_tracker.set_voltage(DV_CELL3, new_v_cell3 - new_v_cell2);

    voltage_tracker.set_voltage(V_BATT, new_v_cell3);
}

void voltage_sense::handle_calibration() //called very frequently by loop.
{
  if (digitalRead(CALIB_BUTTON)) //I pressed the button, start calibrating.
    {
      float calib_0 = voltage_tracker.get_calib(0);
      float calib_1 = voltage_tracker.get_calib(1);
      float calib_2 = voltage_tracker.get_calib(2);

    if(voltage_tracker.get_triple_calibration() && calib_0 == ADC_REF_NOM && calib_1 == ADC_REF_NOM & calib_2 == ADC_REF_NOM)
    {
      //i'm in triple calibration mode, but the calibration array is exactly the same as the datasheet values... which means i haven't been calibrated.
      float vref_new = calibrate();
      calib_0 = voltage_tracker.get_calib(0);
      calib_1 = voltage_tracker.get_calib(1);
      calib_2 = voltage_tracker.get_calib(2);
      eeprom.write_triple_eeprom(calib_0, calib_1, calib_2);
      disp_8.start_8_seg_sequence(NEW_CALIB);
    }
    else if(!voltage_tracker.get_triple_calibration() && eeprom.get_calibration() == -1.0) //i'm not in triple calibration mode, and i haven't been calibrated.
    {
      float vref_new = calibrate();
      eeprom.write_single_eeprom(vref_new);
      disp_8.start_8_seg_sequence(NEW_CALIB);
    }
    else //I have already been calibrated with something.  reset it.
    {
      //wait untill the button press goes away.
      //This is to maintain commonality with how calibrate() works.
      {
        delay(1);
      }
      //reset all my calibration values as well, so my calibration values that i'm using are in lockstep with the EEPROM.
      voltage_tracker.set_voltage(VREF_GUESS, ADC_REF_NOM);
      voltage_tracker.set_calib(0, ADC_REF_NOM);
      voltage_tracker.set_calib(1, ADC_REF_NOM);
      voltage_tracker.set_calib(2, ADC_REF_NOM);

      eeprom.clear_eeprom();
      disp_8.start_8_seg_sequence(CLEAR_CALIB);
    }
  }
}

float voltage_sense::calibrate() //calibrates the device.
//assumes that a 5V line has been put to each battery cell.
//it then calculates its best guess for vref.
{
    //wait untill the button press goes away.
    //This is jank debouncing.
    //Have to calibrate AFTER the button is pressed, not while.  Yes, it's wierd.  PCB issue.
    while (digitalRead(CALIB_BUTTON))
    {
      delay(1);
    }
    delay(100);

    //ok.  let's assume (for now) that every line has 5V put at it.
    //I want to calculate the best-fit for the true vref.

    //expected voltages, after the resistive dividers.
    float expected_vc1 = EXT_CALIB_VOLT * R5 / (R2 + R5);
    float expected_vc2 = EXT_CALIB_VOLT * R6 / (R3 + R6);
    float expected_vc3 = EXT_CALIB_VOLT * R7 / (R4 + R7);

    int r_cell1 = analogRead(CELL1);
    int r_cell2 = analogRead(CELL2);
    int r_cell3 = analogRead(CELL3);

    //as per whiteboard math.
    float vref1 = ADC_COUNTS / (float(r_cell1)) * R5 / (R2 + R5) * EXT_CALIB_VOLT;
    float vref2 = ADC_COUNTS / (float(r_cell2)) * R6 / (R3 + R6) * EXT_CALIB_VOLT;
    float vref3 = ADC_COUNTS / (float(r_cell3)) * R7 / (R4 + R7) * EXT_CALIB_VOLT;

    //calibration array values are updated.  These are only used if triple calibration is in use.
    voltage_tracker.set_calib(0, vref1);
    voltage_tracker.set_calib(1, vref2);
    voltage_tracker.set_calib(2, vref3);

    //avg all vrefs together to get best guess value
    float vref_guess = (vref1 + vref2 + vref3) / 3.0f;
    voltage_tracker.set_voltage(VREF_GUESS, vref_guess);
    return vref_guess;
}
