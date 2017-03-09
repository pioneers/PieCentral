#include "eeprom.h"

//low-level functions that deal with storing the calibration values using the agreed upon format.

float get_calibration()  //returns calibration voltage.  Returns -1 (float) if no calibration.
{
   if(EEPROM.read(0)=='C' && EEPROM.read(1)=='A' && EEPROM.read(2)=='L' && EEPROM.read(3)==':')
   {
      //instantiate a float.
      float f = 0.0f;
      EEPROM.get(4,f); //calibration value is stored in location 4
      return f;
   }
   else
   {
      return -1.0;
   }
}


void update_triple_calibration() //updates the global "calib" array based on EEPROM.
//Calib will contain datasheet values (2.56) if there's no calibration.
//If there is, the appopriate elements will be updated.
{
  int next_addr = 0;
  for(int i = 1; i<=3; i++)
  {
     if(EEPROM.read(next_addr)=='C' && EEPROM.read(next_addr+1)=='A' && EEPROM.read(next_addr+2)=='L' && EEPROM.read(next_addr+3) == char(i+'0') &&EEPROM.read(next_addr+4)==':')
     //so i only take a valid calibration, and there's no chance of accidentally getting messed up with partial triple calibration left over in single mode.
     {
        //instantiate a float.
        float f = 0.0f;
        EEPROM.get(next_addr+5,f); //calibration value is stored in location 4
        calib[i-1] = f; //put value into the calibration array.
        next_addr = next_addr+5+sizeof(float);
     }
     else
     {
        return;
     }
  }
}


void write_single_eeprom(float val)
{
  //write one-value calibration to eeprom in the following format:
  //This code may not be used in three-calibration mode, which will be standard.
  EEPROM.write(0, 'C');
  EEPROM.write(1, 'A');
  EEPROM.write(2, 'L');
  EEPROM.write(3, ':');

  //needs arduino 1.6.12 or later.
  EEPROM.put(4,val);
}


void write_triple_eeprom(float val1, float val2, float val3)
{
  //write one-value calibration to eeprom in the following format:
  //"CAL1:<float1>CAL2:<float2>CAL3<float3> 

  int next_addr = 0;
  for(int i = 1; i<=3; i++)
  {
    EEPROM.write(next_addr,'C');
    next_addr++;
    EEPROM.write(next_addr, 'A');
    next_addr++;
    EEPROM.write(next_addr, 'L');
    next_addr++;
    EEPROM.write(next_addr, char(i+'0'));
    next_addr++;
    EEPROM.write(next_addr,':');
    next_addr++;
    if(i ==1)
    {
      EEPROM.put(next_addr,val1);
    }
    else if(i == 2)
    {
      EEPROM.put(next_addr,val2);
    }
    else if(i == 3)
    {
      EEPROM.put(next_addr,val3);
    }
    next_addr = next_addr + sizeof(float);
  }
}

void clear_eeprom()
{
  for (int i = 0 ; i < EEPROM.length() ; i++) 
  {
    EEPROM.write(i, 0);
  }
}

