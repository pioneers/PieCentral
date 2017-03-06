#ifndef METAL_DET_H
#define METAL_DET_H

#include "hibike_device.h"

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  METAL_DETECTOR,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

#define TRIG_PIN 2

// the last stored measurements or over 5*16 measurments
#define MEASURE_EVERY 5
#define HISTORY_LEN 16  // Power of 2
#define HISTORY_INDEX_MASK 0x0F  // = HISTORY_LEN-1

// function prototypes
void setup();
void loop();
uint32_t getReading();
void initDetector();
void initIsr();
ISR(INT0_vect);


#endif /* METAL_DET_H */
