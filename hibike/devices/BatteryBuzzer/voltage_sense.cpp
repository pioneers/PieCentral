#include "voltage_sense.h"
#include "pdb_defs.h"

float v_cell1;  // param 1
float v_cell2;  // param 2
float v_cell3;  // param 3
float v_batt;   // param 4
float dv_cell2; // param 5
float dv_cell3; // param 6

//code that deals with measuring cell voltages.
//also deals with calibration.

void setup_sensing()
{
  pinMode(ENABLE, OUTPUT);
  pinMode(CALIB_BUTTON, INPUT);

  //for stable (if unknown) internal voltage.
  analogReference(INTERNAL);

  //let's turn enable on, so we can measure the battery voltage.
  digitalWrite(ENABLE, HIGH);

  if(triple_calibration)
  {
    update_triple_calibration();  //and then update the calibration values I use based on what I now know
  }
  else
  {
    float val = get_calibration();
    if(val > 0) //by convention, val is -1 if there's no calibration.
    {
      vref_guess = val;   
    }
  }  
}


void measure_cells() //measures the battery cells. Should call at least twice a second, but preferrably 5x a second.  No use faster.
{
    int r_cell1 = analogRead(CELL1);
    int r_cell2 = analogRead(CELL2);
    int r_cell3 = analogRead(CELL3);

    v_cell1 = float(r_cell1) * (R2 + R5) / R5 * calib[0] / ADC_COUNTS;
    v_cell2 = float(r_cell2) * (R3 + R6) / R6 * calib[1] / ADC_COUNTS;
    v_cell3 = float(r_cell3) * (R4 +  R7) / R7 * calib[2] / ADC_COUNTS;
  
    dv_cell2 = v_cell2 - v_cell1;
    dv_cell3 = v_cell3 - v_cell2;

    v_batt = v_cell3;
}

void handle_calibration() //called very frequently by loop.
{
  if (digitalRead(CALIB_BUTTON)) //I pressed the button, start calibrating.
    {
    if(triple_calibration && calib[0] == ADC_REF_NOM && calib[1] == ADC_REF_NOM & calib[2] == ADC_REF_NOM)
    {
      //i'm in triple calibration mode, but the calibration array is exactly the same as the datasheet values... which means i haven't been calibrated.
      float vref_new = calibrate();
      write_triple_eeprom(calib[0],calib[1],calib[2]);
      start_8_seg_sequence(NEW_CALIB); 
    }
    else if(!triple_calibration && get_calibration() == -1.0) //i'm not in triple calibration mode, and i haven't been calibrated.
    {   
      float vref_new = calibrate();
      write_single_eeprom(vref_new);
      start_8_seg_sequence(NEW_CALIB);
    }
    else //I have already been calibrated with something.  reset it.
    {
      //wait untill the button press goes away.
      //This is to maintain commonality with how calibrate() works.
      {
        delay(1);
      }
      //reset all my calibration values as well, so my calibration values that i'm using are in lockstep with the EEPROM.
      vref_guess = ADC_REF_NOM;
      calib[0] = ADC_REF_NOM;
      calib[1] = ADC_REF_NOM;
      calib[2] = ADC_REF_NOM;

      clear_eeprom();
      start_8_seg_sequence(CLEAR_CALIB);
    }
  }
}

float calibrate() //calibrates the device.
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
    calib[0] = vref1;
    calib[1] = vref2;
    calib[2] = vref3;

    //avg all vrefs together to get best guess value    
    vref_guess = (vref1 + vref2 + vref3) / 3.0f;
    return vref_guess;
}

