#include "eeprom.h"

//Class for low-level functions that deal with storing the calibration values.
eeprom::eeprom(VoltageTracker v_tracker)
{
  VoltageTracker eeprom::voltage_tracker = v_tracker;
}

// Returns calibration voltage.  Returns -1 (as float) if no calibration.
float eeprom::get_calibration()
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


void eeprom::update_triple_calibration() //updates the global "calib" array based on EEPROM.
//Calib will contain datasheet values (2.56) if there's no calibration.
//If there is, the appopriate elements will be updated.
{
  int next_addr = 0;
  for(int i = 1; i<=3; i++)
  {
    char first = EEPROM.read(next_addr);
    char second = EEPROM.read(next_addr + 1);
    char third = EEPROM.read(next_addr + 2);
    char fourth = EEPROM.read(next_addr + 3);
    char fifth = EEPROM.read(next_addr + 4);
    if(first == 'C' && second == 'A' && third == 'L' && fourth == char(i+'0') && fifth == ':')
    // Only takes in a valid calibration -  no chance of using partial triple calibration left over in single mode.
    {
      //instantiate a float.
      float f = 0.0f;
      EEPROM.get(next_addr + 5,f); //calibration value is stored in location 4
      eeprom::voltage_tracker.set_calib(i - 1, f); // put value into the calibration array
      next_addr = next_addr + 5 + sizeof(float);
    }
      else
    {
      return;
    }
  }
}


void eeprom::write_single_eeprom(float val)
{
  //Write one-value calibration to eeprom in the following format.
  //This code may not be used in three-calibration mode, which will be standard.
  EEPROM.write(0, 'C');
  EEPROM.write(1, 'A');
  EEPROM.write(2, 'L');
  EEPROM.write(3, ':');

  //Needs arduino 1.6.12 or later.
  EEPROM.put(4, val);
}


void eeprom::write_triple_eeprom(float val1, float val2, float val3)
{
  // Write one-value calibration to eeprom in the following format:
  // "CAL1:<float1>CAL2:<float2>CAL3<float3>

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
    if(i == 1)
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

void eeprom::clear_eeprom()
{
  // Writes 0 into all positions of the eeprom.
  for (int i = 0 ; i < EEPROM.length() ; i++)
  {
    EEPROM.write(i, 0);
  }
}
