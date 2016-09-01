#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"
#include "Adafruit_TCS34725.h"

#define DEFAULT_INTEGRATION_TIME TCS34725_INTEGRATIONTIME_50MS
#define DEFAULT_GAIN TCS34725_GAIN_4X

#define TOGGLE_PIN IO2
//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  COLOR_SENSOR,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////
typedef enum {
  INTEGRATION_TIME,
  GAIN,
  TOGGLE
} param;


#define NUM_PARAMS 7


// function prototypes
void setup();
void loop();


#endif /* EX_DEVICE_H */