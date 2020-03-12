#ifndef DISP_8_H
#define DISP_8_H

#include "battery_buzzer.h"

typedef enum {
  NORMAL_VOLT_READ,
  CLEAR_CALIB,
  NEW_CALIB
} SEQ_NUM;

void start_8_seg_sequence(SEQ_NUM sequence_num);

void handle_8_segment();

void test_display();

void setup_display();

#endif

