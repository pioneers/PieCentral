#ifndef SAFETY_H
#define SAFETY_H

#include "VoltageTracker.h"
#include <Arduino.h>

class safety
{
public:

  safety (VoltageTracker& v_tracker, int safety_buzzer);

  void handle_safety();
  bool is_unsafe();
  void buzz(bool should_buzz);

private:
  bool unsafe_status;

  const float min_cell = 3.3;
  const float end_undervolt = 3.6; //I have to exceed this value to remove my undervolt condition.  (Aka if loading conditions momentarily spiked the battery...)
  bool under_volt; //if i undervolt, i'll have to keep track if i'm no longer in an undervolt condition to avoid momentary beeps.

  const float max_cell = 4.4;

  const float d_cell = 0.3; //max voltage difference between cells.
  const float end_d_cell = 0.1; //imbalance must be less than this before i'm happy again.
  bool imbalance;

  int buzzer;

  VoltageTracker voltage_tracker;

  bool compute_safety();
};

#endif
