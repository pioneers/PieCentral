#include "potentiometer.h"

uint8_t pins[NUM_PINS] = {IN_0, IN_1, IN_2};

void setup() {
  hibike_setup(); //use default heartbeat rates. look at /lib/hibike/hibike_device.cpp for exact values
  // Setup sensor input
  for (int i = 0; i < NUM_PINS; i++) {
    pinMode(pins[i], INPUT);
  }
}


void loop() {
  hibike_loop();
}


// You must implement this function.
// It is called when the device receives a Device Write packet.
// Updates param to new value passed in data.
//    param   -   Parameter index
//    data    -   value to write, in little-endian bytes
//    len     -   number of bytes in data
//
//   return  -   size of bytes written on success; otherwise return 0

uint32_t device_write(uint8_t param, uint8_t* data, size_t len){
  return 0;
}


// You must implement this function.
// It is called when the device receives a Device Data packet.
// Modifies data_update_buf to contain the parameter value.
//    param           -   Parameter index
//    data            -   buffer to return data in, little-endian
//    len             -   length of the buffer left to write to
//
//    return          -   sizeof(param) on success; 0 otherwise

uint8_t device_read(uint8_t param, uint8_t* data, size_t len) {
  // Read sensor, which is in uint16
  if (len < sizeof(float) || param > 2) {
    return 0;
  }
  float *data_float = (float *)data;
  data_float[0] = ((float)analogRead(pins[param])) / 1023;
  return sizeof(float);
}

// You must implement this function.
// It is called when the BBB sends a message to the Smart Device tellinng the Smart Device to disable itself.
// Consult README.md, section 6, to see what exact functionality is expected out of disable.
void device_disable() {
//Do nothing.  This is a sensor.
}
