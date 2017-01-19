#include "example_device.h"

// each device is responsible for keeping track of it's own params
uint8_t value0;
uint8_t value1;
uint16_t value2;
uint32_t value3;
uint64_t value4;
uint64_t value5;


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
  value1 += 1;
  value2 += 2;
  value3 += 3;
  value4 += 4;
  value5 += 5;

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

uint32_t device_write(uint8_t param, uint8_t* data, size_t len) {
  switch (param) {
    case VALUE_0:
      value0 = (uint8_t) read_num_bytes(data, sizeof(value0));
      return sizeof(value0);
      break;
    case VALUE_1:
      value1 = (uint8_t) read_num_bytes(data, sizeof(value1));
      return sizeof(value1);
      break;
    case VALUE_2:
      value2 = (uint16_t) read_num_bytes(data, sizeof(value2));
      return sizeof(value2);
      break;
    case VALUE_3:
      value3 = (uint32_t) read_num_bytes(data, sizeof(value3));
      return sizeof(value3);
      break;
    case VALUE_4:
      value4 = (uint64_t) read_num_bytes(data, sizeof(value4));
      return sizeof(value4);
      break;
    case VALUE_5:
      value5 = (uint64_t) read_num_bytes(data, sizeof(value5));
      return sizeof(value5);
      break;
    default:
      return 0;
  }
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
  switch (param) {
    case VALUE_0:
      write_num_bytes(value0, data_update_buf, sizeof(value0));
      return sizeof(value0);
      break;
    case VALUE_1:
      write_num_bytes(value1, data_update_buf, sizeof(value1));
      return sizeof(value1);
      break;
    case VALUE_2:
      write_num_bytes(value2, data_update_buf, sizeof(value2));
      return sizeof(value2);
      break;
    case VALUE_3:
      write_num_bytes(value3, data_update_buf, sizeof(value3));
      return sizeof(value3);
      break;
    case VALUE_4:
      write_num_bytes(value4, data_update_buf, sizeof(value4));
      return sizeof(value4);
      break;
    case VALUE_5:
      write_num_bytes(value5, data_update_buf, sizeof(value5));
      return sizeof(value5);
      break;
    default:
      return 0;
  }
  return 0;
}
