#include "voltage_sense.h"

//code that deals with measuring cell voltages.
//also deals with calibration.

int cell1 = A0;
int cell2 = A1;
int cell3 = A2;

int enable = 16;
int calib_button = 21;



void setup_sensing()
{

  pinMode(enable, OUTPUT);
  pinMode(calib_button, INPUT);

  

  //for stable (if unknown) internal voltage.
  analogReference(INTERNAL);

  //let's turn enable on, so we can measure the battery voltage.
  digitalWrite(enable, HIGH);

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
    int r_cell1 = analogRead(cell1);
    int r_cell2 = analogRead(cell2);
    int r_cell3 = analogRead(cell3);

    //Serial.println("Raw Voltages");
    //Serial.println(5*float(r_cell1)/1024);
    //Serial.println(5*float(r_cell2)/1024);
    //Serial.println(5*float(r_cell3)/1024);


    v_cell1 = float(r_cell1) * (10 + 10.0) / 10.0 * calib[0] / 1024;  // (10k + 10k)/(10k) to extract cell voltage in counts, then convert 1024 counts per vref volts.
    v_cell2 = float(r_cell2) * (30.0 + 10) / 10.0 * calib[1] / 1024;  // (30k + 10k)/(10k) to extract cell voltage in counts, then convert 1024 counts per vref volts.
    v_cell3 = float(r_cell3) * (51.00 + 10.0 ) / 10.0 * calib[2] / 1024;  // (51k + 10k)/(10k) to extract cell voltage in counts, then convert 1024 counts per vref volts.
  
    dv_cell2 = v_cell2 - v_cell1;
    dv_cell3 = v_cell3 - v_cell2;

    v_batt = v_cell3;

    // if(prints)
    // {
    //   String str_cell1 = String(v_cell1, 3);
    //   String str_cell2 = String(v_cell2, 3);
    //   String str_cell3 = String(v_cell3, 3);
  
  
  
    //   String sdv_cell2 = String(dv_cell2, 3);
    //   String sdv_cell3 = String(dv_cell3, 3);
  

    //   if(triple_calibration)
    //   {
    //     Serial.println("Triple Calibration Mode");
    //   }
    //   else
    //   {
    //     Serial.println("Single Calibration Mode");
    //   }
  
    //   Serial.println("ABS: Cell1 : " + str_cell1 + " Cell2 : " + str_cell2 + " Cell3 : " + str_cell3);
    //   Serial.println("REL: Cell1: " + str_cell1 + " Cell2 : " + sdv_cell2 + " Cell3 : " + sdv_cell3);
    //   Serial.println("");
    //   Serial.println("");


    // }
    last_print_time = millis();

}

void handle_calibration() //called very frequently by loop.
{
  if (digitalRead(calib_button)) //I pressed the button, start calibrating.
    {
    if(triple_calibration && calib[0] == 2.56 && calib[1] == 2.56 & calib[2] == 2.56)
    {
      //i'm in triple calibration mode, but the calibration array is exactly the same as the datasheet values... which means i haven't been calibrated.
      float vref_new = calibrate();
      write_triple_eeprom(calib[0],calib[1],calib[2]);
      start_8_seg_sequence(2); 
    }
    else if(!triple_calibration && get_calibration() == -1.0) //i'm not in triple calibration mode, and i haven't been calibrated.
    {   
      float vref_new = calibrate();
      write_single_eeprom(vref_new);
      start_8_seg_sequence(2);
    }
    else //I have arleady been calibrated with something.  reset it.
    {
      //wait untill the button press goes away.
      //This is to maintain commonality with how calibrate() works.
      {
        delay(1);
      }
      
      if(prints)
      {
        Serial.println("Clear EEPROM");
      }
      //reset all my calibration values as well, so my calibration values that i'm using are in lockstep with the EEPROM.
      
      vref_guess = 2.56;
      calib[0] = 2.56;
      calib[1] = 2.56;
      calib[2] = 2.56;


      clear_eeprom();
      start_8_seg_sequence(1);
      

    }
  }
}

float calibrate() //calibrates the device.
//assumes that a 5V line has been put to each battery cell.
//it then calculates its best guess for vref.
{
    if(prints)
    {
      Serial.println("I Should calibrate now");
    }

    //wait untill the button press goes away.
    //This is jank debouncing.
    //Have to calibrate AFTER the button is pressed, not while.  Yes, it's wierd.  PCB issue.
    while (digitalRead(calib_button))
    {
      delay(1);
    }
    delay(100);


    //ok.  let's assume (for now) that every line has 5V put at it.
    //I want to calculate the best-fit for the true vref.

    //expected voltages, after the resistive dividers.
    float expected_vc1 = 5 * 10.0 / (10.00 + 10.00);
    float expected_vc2 = 5 * 10.0 / (30.00 + 10.00);
    float expected_vc3 = 5 * 10.0 / (51.00 + 10.0);


    int r_cell1 = analogRead(cell1);
    int r_cell2 = analogRead(cell2);
    int r_cell3 = analogRead(cell3);


    //as per whiteboard math.  Is it 1023 or 1024?  I think it's 1023.
    float vref1 = 1024 / (float(r_cell1)) * 10.0 / (10.0 + 10.00) * 5;
    float vref2 = 1024 / (float(r_cell2)) * 10.0 / (30.0 + 10.0) * 5;
    float vref3 = 1024 / (float(r_cell3)) * 10.0 / (51.00 + 10.0) * 5;

    //calibration array values are updated.  These are only used if triple calibration is in use.
    calib[0] = vref1;
    calib[1] = vref2;
    calib[2] = vref3;


    //avg all vrefs together to get best guess value    
    vref_guess = (vref1 + vref2 + vref3) / float(3);
    
    // if(prints)
    // {
    //   if(triple_calibration)
    //   {
    //     Serial.print("vref1 :");
    //     Serial.println(vref1);
    //     Serial.print("vref2 :");
    //     Serial.println(vref2);
    //     Serial.print("vref3 :");
    //     Serial.println(vref3);
    //   }
    //   else
    //   {
    //     Serial.println("Vref Guess is " + String(vref_guess, 4));
    //   }
    // }



    return vref_guess;

}