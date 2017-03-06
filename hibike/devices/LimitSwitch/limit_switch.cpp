#include "limit_switch.h"

uint8_t pins[NUM_SWITCHES] = {IN_0, IN_1, IN_2};

void setup() {
  hibike_setup();
  // Setup sensor input
  for (int i = 0; i < NUM_SWITCHES; i++) {
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
//    data    -   value to write, in bytes, little-endian
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

  if (MAX_PAYLOAD_SIZE - len < sizeof(uint8_t) || param >= NUM_SWITCHES || param<0) {
    return 0;
  }
  data[0] = digitalRead(pins[param]) == LOW;
  return sizeof(bool);

}
