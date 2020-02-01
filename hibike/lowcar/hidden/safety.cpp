#include "safety.h"
#include "pitches.h"

//Determines if the battery is safe or not, and takes appropriate action.
//Code is regularly called (currently every 250ms)

safety::safety(VoltageTracker v_tracker, int safety_buzzer) {
  bool unsafe_status = false;

  const float min_cell = 3.3;
  const float end_undervolt = 3.6; //I have to exceed this value to remove my undervolt condition.  (Aka if loading conditions momentarily spiked the battery...)
  bool under_volt = false; //if i undervolt, i'll have to keep track if i'm no longer in an undervolt condition to avoid momentary beeps.

  const float max_cell = 4.4;

  const float d_cell = .3; //max voltage difference between cells.
  const float end_d_cell = 0.1; //imbalance must be less than this before i'm happy again.
  bool imbalance = false;

  int buzzer = safety_buzzer;

  VoltageTracker voltage_tracker = v_tracker;
}

bool safety::compute_safety() //returns if i'm safe or not based on the most recent reading.
//Currently does only over and under voltage protection.  No time averaging.  So will need to be fancier later.
{
  float v_cell1 = voltage_tracker.get(V_CELL1);
  float dv_cell2 = voltage_tracker.get(DV_CELL2);
  float dv_cell3 = voltage_tracker.get(DV_CELL3);

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
    tone(buzzer, NOTE_A5);
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
