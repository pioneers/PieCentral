#include "potentiometer.h"
#include <Servo.h>

uint8_t pins[NUM_PINS] = {IN_0, IN_1, IN_2};

void setup() {
  hibike_setup();

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
// It is called when the device receives a Device Data Update packet.
// Modifies data_update_buf to contain the parameter value.
//    param           -   Parameter index
//    data_update_buf -   buffer to return data in, little-endian
//    buf_len         -   Maximum length of the buffer
//
//    return          -   sizeof(param) on success; 0 otherwise

uint8_t device_data_update(uint8_t param, uint8_t* data_update_buf, size_t buf_len) {
  // Read sensor, which is in uint16
  if (MAX_PAYLOAD_SIZE - buf_len < sizeof(float) || param > 2) {
    return 0;
  }
  float *data = (float *)data_update_buf;
  data[0] = ((float)analogRead(pins[param])) / 1023;
  return sizeof(float);
}
