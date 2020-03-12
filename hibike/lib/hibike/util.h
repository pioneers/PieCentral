#ifndef UTIL_H
#define UTIL_H

#include <stdint.h>
#include <string.h>

uint64_t read_num_bytes(uint8_t* data, size_t num);
void write_num_bytes(uint64_t data, uint8_t* data_buf, size_t num);

#endif /* UTIL_H */
