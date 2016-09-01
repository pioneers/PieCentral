#include "limit_switch.h"



uint8_t pins[NUM_SWITCHES] = {IN_0, IN_1, IN_2, IN_3};

void setup() {
  hibike_setup();
  // Setup sensor input
  for (int i = 0; i < NUM_SWITCHES; i++) {
    pinMode(pins[i], INPUT_PULLUP);
  }

}


void loop() {
  hibike_loop();
}

// you must implement this function. It is called when the device receives a DeviceUpdate packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_update(uint8_t param, uint32_t value) {
  return ~((uint32_t) 0);
}

// you must implement this function. It is called when the devie receives a DeviceStatus packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_status(uint8_t param) {
  return ~((uint32_t) 0);
}


// you must implement this function. It is called with a buffer and a maximum buffer size.
// The buffer should be filled with appropriate data for a DataUpdate packer, and the number of bytes
// added to the buffer should be returned. 
//
// You can use the helper function append_buf.
// append_buf copies the specified amount data into the dst buffer and increments the offset
uint8_t data_update(uint8_t* data_update_buf, size_t buf_len) {

  if (buf_len < sizeof(uint8_t) * NUM_SWITCHES) {
    return 0;
  }

  uint8_t *data = (uint8_t *) data_update_buf;
  // Read sensor
  for (int i = 0; i < NUM_SWITCHES; i++) {
      data[i] = 1 - digitalRead(pins[i]);  
  }
  return sizeof(uint8_t) * NUM_SWITCHES;

}
