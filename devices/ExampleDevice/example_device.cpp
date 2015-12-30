#include "example_device.h"

uint32_t params[NUM_PARAMS];
uint8_t value0;
uint8_t value1;
uint16_t value2;
uint32_t value3;
uint64_t value4;

void setup() {
  hibike_setup();
  memset(&params, 0, sizeof(params[0])*NUM_PARAMS);
}

void loop() {
  // Read sensor
  value0++;
  value1++;
  value2++;
  value3++;
  value4++;

  hibike_loop();
}

uint32_t device_update(uint8_t param, uint32_t value) {
  param -= 1;
  if (param < NUM_PARAMS) {
    params[param] = value;
    return params[param];
  }
  return ~((uint32_t) 0);
}

uint32_t device_status(uint8_t param) {
  param -= 1;
  if (param < NUM_PARAMS) {
    return params[param];
  }
  return ~((uint32_t) 0);
}

uint8_t data_update(uint8_t* data_update_buf, size_t buf_len) {
  uint8_t offset = 0;
  append_buf(data_update_buf, &offset, (uint8_t *)&value0, sizeof(value0));
  append_buf(data_update_buf, &offset, (uint8_t *)&value1, sizeof(value1));
  append_buf(data_update_buf, &offset, (uint8_t *)&value2, sizeof(value2));
  append_buf(data_update_buf, &offset, (uint8_t *)&value3, sizeof(value3));
  append_buf(data_update_buf, &offset, (uint8_t *)&value4, sizeof(value4));
  return offset;
}

