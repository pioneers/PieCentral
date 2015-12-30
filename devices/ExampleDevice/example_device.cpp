#include "example_device.h"

// each device is responsible for keeping track of it's own params
uint32_t params[NUM_PARAMS];


uint8_t value0;
uint8_t value1;
uint16_t value2;
uint32_t value3;
uint64_t value4;

// normal arduino setup function, you must call hibike_setup() here
void setup() {
  hibike_setup();
}

// normal arduino loop function, you must call hibike_loop() here
// hibike_loop will look for any packets in the serial buffer and handle them
void loop() {

  // do whatever you want here
  // note that hibike will only process one packet per call to hibike_loop()
  // so exessive delays here will affect hibike.
  value1++;
  value2++;
  value3++;
  value4++;

  hibike_loop();
}


// you must implement this function. It is called when the device receives a DeviceUpdate packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_update(uint8_t param, uint32_t value) {
  if (param < NUM_PARAMS) {
    params[param] = value;
    return params[param];
  }
  return ~((uint32_t) 0);
}

// you must implement this function. It is called when the devie receives a DeviceStatus packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_status(uint8_t param) {
  if (param < NUM_PARAMS) {
    return params[param];
  }
  return ~((uint32_t) 0);
}


// you must implement this function. It is called with a buffer and a maximum buffer size.
// The buffer should be filled with appropriate data for a DataUpdate packer, and the number of bytes
// added to the buffer should be returned. 
//
// You can use the helper function append_buf.
// append_buf copies the specified amount data into the dst buffer and increments the offset
uint8_t data_update(uint8_t* data_update_buf, size_t buf_len) {
  uint8_t offset = 0;
  append_buf(data_update_buf, &offset, (uint8_t *)&value0, sizeof(value0));
  append_buf(data_update_buf, &offset, (uint8_t *)&value1, sizeof(value1));
  append_buf(data_update_buf, &offset, (uint8_t *)&value2, sizeof(value2));
  append_buf(data_update_buf, &offset, (uint8_t *)&value3, sizeof(value3));
  append_buf(data_update_buf, &offset, (uint8_t *)&value4, sizeof(value4));
  return offset;
}

