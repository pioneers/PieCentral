#ifndef DISP_8_H
#define DISP_8_H

#include <SevenSeg.h>
#include "VoltageTracker.h"
#include "pdb_defs.h"

const int numOfDigits = 4;
SevenSeg disp = new SevenSeg(A, B, C, D, E, G, H); // Not alphabetical because Arduino overrides F

class disp_8
{
public:

  disp_8 (VoltageTracker v_tracker);

  void start_8_seg_sequence(SEQ_NUM sequence_num);

  void handle_8_segment();

  void test_display();

  void setup_display();

private:

  int digitPins[numOfDigits];

  unsigned long last_LED_time;  //Time the last LED switched
  int sequence; //used to switch states for the display.  Remember that the hangle_8_segment cannot be blocking.

  SEQ_NUM segment_8_run;  //0 for the normal voltage readout.  1 for "Clear Calibration".  2 for "New Calibration"

  VoltageTracker voltage_tracker;
};

#endif
