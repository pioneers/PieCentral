#include "util.h"

// Assumes little endian

uint64_t read_num_bytes(uint8_t* data, size_t num) {
  uint64_t value = 0;
  for (size_t i = 0; i < num; i++) {
    value += data[i] << (8 * i);
  }
  return value;
}


// Assumes little endian

void write_num_bytes(uint64_t data, uint8_t* data_buf, size_t num) {
  for (size_t i = 0; i < num; i++) {
    data_buf[i] = (uint8_t) (data >> (8 * i));
  }
}
