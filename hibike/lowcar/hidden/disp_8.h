#ifndef DISP_8_H
#define DISP_8_H

#include <SevenSeg.h>
#include "VoltageTracker.h"

const int numOfDigits = 4;
SevenSeg disp = SevenSeg(A, B, C, D, E, F, G);

class disp_8
{
public:

  typedef enum {
    NORMAL_VOLT_READ,
    CLEAR_CALIB,
    NEW_CALIB
  } SEQ_NUM;

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
