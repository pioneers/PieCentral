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

uint32_t device_write(uint8_t param, uint8_t* data, size_t len){
  return 0;
}


// you must implement this function. It is called with a buffer and a maximum buffer size.
// The buffer should be filled with appropriate data for a DataUpdate packer, and the number of bytes
// added to the buffer should be returned. 
//
// You can use the helper function append_buf.
// append_buf copies the specified amount data into the dst buffer and increments the offset


uint8_t device_data_update(int param, uint8_t* data_update_buf, size_t buf_len) {

  if (MAX_PAYLOAD_SIZE - buf_len < sizeof(uint8_t) || param >= NUM_SWITCHES) {
    return 0;
  }
  data_update_buf[0] = 1 - digitalRead(pins[param]);
  return sizeof(uint8_t);

}
// uint8_t data_update(uint8_t* data_update_buf, size_t buf_len) {

//   if (buf_len < sizeof(uint8_t) * NUM_SWITCHES) {
//     return 0;
//   }

//   uint8_t *data = (uint8_t *) data_update_buf;
//   // Read sensor
//   for (int i = 0; i < NUM_SWITCHES; i++) {
//       data[i] = 1 - digitalRead(pins[i]);  //what does this do
//   }
//   return sizeof(uint8_t) * NUM_SWITCHES;

// }
