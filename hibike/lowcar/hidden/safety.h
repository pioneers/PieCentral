#ifndef SAFETY_H
#define SAFETY_H

#include "VoltageTracker.h"

class safety
{
public:

  safety (VoltageTracker v_tracker, int buzzer);

  void handle_safety();
  bool is_unsafe();

private:
  bool unsafe_status;

  const float min_cell;
  const float end_undervolt; //I have to exceed this value to remove my undervolt condition.  (Aka if loading conditions momentarily spiked the battery...)
  bool under_volt; //if i undervolt, i'll have to keep track if i'm no longer in an undervolt condition to avoid momentary beeps.

  const float max_cell;

  const float d_cell; //max voltage difference between cells.
  const float end_d_cell; //imbalance must be less than this before i'm happy again.
  bool imbalance;

  VoltageTracker voltage_tracker;
};

#endif
