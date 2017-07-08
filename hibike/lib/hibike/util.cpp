/* Licensed to Pioneers in Engineering under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Pioneers in Engineering licenses
 * this file to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 *  with the License.  You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 */ under the License
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
