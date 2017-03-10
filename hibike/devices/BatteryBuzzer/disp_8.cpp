//code that deals with displaying the data to the outside world.

#include <SevenSeg.h>
#include "disp_8.h"
#include "pdb_defs.h"

//Segment Pins, A to G
SevenSeg disp(A,B,C,D,E,F,G);

const int numOfDigits=4;
int digitPins[numOfDigits] = {DISP_PIN_1, DISP_PIN_2, DISP_PIN_3, DISP_PIN_4};

unsigned long last_LED_time = 0;  //Time the last LED switched
int sequence = 0; //used to switch states for the display.  Remember that the hangle_8_segment cannot be blocking.

SEQ_NUM segment_8_run = NORMAL_VOLT_READ;  //0 for the normal voltage readout.  1 for "Clear Calibration".  2 for "New Calibration"


void setup_display()
{
  disp.setDigitPins(numOfDigits,digitPins);
  disp.setDPPin(DECIMAL_POINT);  //set the Decimal Point pin to #1   
}


void test_display() //a function to ensure that all outputs of the display are working.
//On the current PDB, this should display "8.8.8.8."  The library is capable of handling : and ', but the wires are not hooked up to it.
{
  for(int i = 0; i<250; i++)
  {
    disp.write("8.8.8.8."); //this function call takes a surprising amount of time, probably because of how many characters are in it.
  }
  disp.clearDisp();
}


void handle_8_segment() //handles the 8-segment display, and prints out the global values.
//MUST be called in the loop() without any if's
{
  if(segment_8_run == NORMAL_VOLT_READ)
  {
    //Shows text / numbers of all voltages & then individual cells.
    //Changed every Second
    if(sequence == 0)
    {
      disp.write("ALL");
    }
    else if(sequence == 1)
    {
      disp.write(v_batt,2);
    }
    else if(sequence == 2)
    {
      disp.write("CEL.1"); 
    }
    else if(sequence == 3)
    {
      disp.write(v_cell1,2);
    }
    else if(sequence == 4)
    {
      disp.write("CEL.2"); 
    }
    else if(sequence == 5)
    {
      disp.write(dv_cell2,2);
    }
    else if(sequence == 6)
    {
      disp.write("CEL.3"); 
    }
    else if(sequence == 7)
    {
      disp.write(dv_cell3,2);
    }
    
    if (millis() > (last_LED_time + 1000) ) //every second
    {
      sequence = sequence + 1;
      if(sequence == 8)
      {
        sequence=0;
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
        start_8_seg_sequence(0); //return to default Programming... showing battery voltages.
      }
      last_LED_time = millis();
    }

  }
  else if(segment_8_run == NEW_CALIB)
  {
    if(triple_calibration)
    {
      if(sequence == 0)
      {
        disp.write("CAL");
      }
      else if(sequence == 1)
      {
        disp.write("DONE");      
      }
      else if(sequence == 2)
      {
        disp.write("CAL.1");
      }
      else if(sequence == 3)
      {
        disp.write(calib[0],3);
      }  
      else if(sequence == 4)
      {
        disp.write("CAL.2");
      }
      else if(sequence == 5)
      {
        disp.write(calib[1],3);
      }
      else if(sequence == 6)
      {
        disp.write("CAL.3");
      }
      else if(sequence == 7)
      {
        disp.write(calib[2],3);
      }

      
      if (millis() > (last_LED_time + 750) ) //every 3/4 second
      {
        sequence = sequence + 1;
        if(sequence == 8)
        {
          start_8_seg_sequence(0); //return to default Programming... showing battery voltages.
        }
        last_LED_time = millis();
      }
      
    }
    else
    {
      if(sequence == 0)
      {
        disp.write("CAL");
      }
      else if(sequence == 1)
      {
        disp.write("DONE");      
      }
      if(sequence == 2)
      {
        disp.write("CAL");
      }
      if(sequence == 3)
      {
        disp.write(vref_guess,3);
      }
      
      if (millis() > (last_LED_time + 750) ) //every 3/4 second
      {
        sequence = sequence + 1;
        if(sequence == 4)
        {
          start_8_seg_sequence(0); //return to default Programming... showing battery voltages.
        }
        last_LED_time = millis();
      }      
    }
  }
}

void start_8_seg_sequence(SEQ_NUM sequence_num)
{
  segment_8_run = sequence_num; //rel the display to run the right sequence
  sequence = 0;  //and reset the step in the sequence to zero.
  last_LED_time = millis();
}

