#include "safety.h"
#include "battery_buzzer.h"
#include "pitches.h"

//has code that determines if the battery is safe or not, and takes appropriate action.
//this code is regularly called (currently every 250ms)
bool unsafe_status = false;

const float min_cell = 3.3;
const float end_undervolt = 3.6; //I have to exceed this value to remove my undervolt condition.  (Aka if loading conditions momentarily spiked the battery...)
bool under_volt = false; //if i undervolt, i'll have to keep track if i'm no longer in an undervolt condition to avoid momentary beeps.


const float max_cell = 4.4;

const float d_cell = .3; //max voltage difference between cells.
const float end_d_cell = 0.1; //imbalance must be less than this before i'm happy again.
bool imbalance = false;

bool compute_safety() //returns if i'm safe or not based on the most recent reading.
//Currently does only over and under voltage protection.  No time averaging.  So will need to be fancier later.
{
  bool unsafe;
  if( (v_cell1 < min_cell ) || (dv_cell2 < min_cell) || (dv_cell3 < min_cell) ) //minimum cell voltages
  {
    unsafe = true;
    under_volt = true;
  }
  else if( (v_cell1 > max_cell ) || (dv_cell2 > max_cell) || (dv_cell3 > max_cell) ) //maximum cell voltages.
  {
    unsafe = true;
  }
  else if( (abs(v_cell1 - dv_cell2) > d_cell) || (abs(dv_cell2 - dv_cell3) > d_cell) || (abs(dv_cell3 - v_cell1) > d_cell) ) //imbalance.
  {
    imbalance = true;
    unsafe = true;
  }
  else if(under_volt && (v_cell1 > end_undervolt ) && (dv_cell2 > end_undervolt) && (dv_cell3 > end_undervolt) ) //i was undervolted but i'm now over the exit threshold.  This has the effect of rejecting momentary dips under the undevolt threshold (say, loading effects) but continuing to be unsafe if i'm hoving close (say, random oscliations)
  {
    unsafe = false;
    under_volt = false;
  }
  else if(imbalance && (abs(v_cell1 - dv_cell2) < end_d_cell) && (abs(dv_cell2 - dv_cell3) < end_d_cell) && (abs(dv_cell3 - v_cell1) < end_d_cell) ) //imbalance. //i was undervolted but i'm now over the exit threshold.  This has the effect of rejecting momentary dips under the undevolt threshold (say, loading effects) but continuing to be unsafe if i'm hoving close (say, random oscliations)
  {
    unsafe = false;
    imbalance = false;
  }
  else
  {
    unsafe = false;
  }
  return unsafe;
}


void buzz(boolean should_buzz)
{
  if(should_buzz)
  {
    tone(buzzer,NOTE_A5);
  }
  else
  {
    noTone(buzzer);
  }
}


void handle_safety()
{
  unsafe_status = compute_safety(); //Currently, just does basic sensing.  Should get updated.
  buzz(unsafe_status);
}

bool is_unsafe()
{
  return unsafe_status;
}

