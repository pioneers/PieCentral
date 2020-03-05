#include "safety.h"
#include "pitches.h"

//Determines if the battery is safe or not, and takes appropriate action.
//Code is regularly called (currently every 250ms)

safety::safety(VoltageTracker& v_tracker, int safety_buzzer) : voltage_tracker(v_tracker)
{
  unsafe_status = false;
  under_volt = false; //if i undervolt, i'll have to keep track if i'm no longer in an undervolt condition to avoid momentary beeps.
  imbalance = false;

  buzzer = safety_buzzer;
}

bool safety::compute_safety() //returns if i'm safe or not based on the most recent reading.
//Currently does only over and under voltage protection.  No time averaging.  So will need to be fancier later.
{
  float v_cell1 = voltage_tracker.get_voltage(V_CELL1);
  float dv_cell2 = voltage_tracker.get_voltage(DV_CELL2);
  float dv_cell3 = voltage_tracker.get_voltage(DV_CELL3);

  bool unsafe;
  // Case 0: Cell voltages are below minimum values.
  if( (v_cell1 < min_cell ) || (dv_cell2 < min_cell) || (dv_cell3 < min_cell) )
  {
    unsafe = true;
    under_volt = true;
  }
  // Case 1: Cell voltages are above maximum values.
  else if((v_cell1 > max_cell ) || (dv_cell2 > max_cell) || (dv_cell3 > max_cell))
  {
    unsafe = true;
  }
  // Case 2: Imbalanced cell voltages.
  else if( (abs(v_cell1 - dv_cell2) > d_cell) || (abs(dv_cell2 - dv_cell3) > d_cell) || (abs(dv_cell3 - v_cell1) > d_cell))
  {
    imbalance = true;
    unsafe = true;
  }
  // Case 3: Previously undervolted, now exceeding exit threshold.  This has the effect of
  // rejecting momentary dips under the undervolt threshold but continuing to be unsafe if hovering close.
  else if(under_volt && (v_cell1 > end_undervolt) && (dv_cell2 > end_undervolt) && (dv_cell3 > end_undervolt) )
  {
    unsafe = false;
    under_volt = false;
  }
  // Case 4: Imbalanced, previously undervolted, and now exceeding exit thresholds.
  else if(imbalance && (abs(v_cell1 - dv_cell2) < end_d_cell) && (abs(dv_cell2 - dv_cell3) < end_d_cell) && (abs(dv_cell3 - v_cell1) < end_d_cell) )
  {
    unsafe = false;
    imbalance = false;
  }
  // Case 5: All is well.
  else
  {
    unsafe = false;
  }
  return unsafe;
}

void safety::buzz(bool should_buzz)
{
  if(should_buzz)
  {
    //tone(buzzer, NOTE_A5);
  }
  else
  {
    noTone(buzzer);
  }
}

void safety::handle_safety()
{
  unsafe_status = compute_safety(); //Currently, just does basic sensing.  Should get updated.
  buzz(unsafe_status);
}

bool safety::is_unsafe()
{
  return unsafe_status;
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
      voltage_tracker.set_calib(i - 1, f); // put value into the calibration array
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
