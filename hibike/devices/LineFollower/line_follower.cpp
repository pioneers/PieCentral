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
#include "line_follower.h"

uint16_t data[NUM_PINS];

void setup() {
  hibike_setup(); //use default heartbeat rates. look at /lib/hibike/hibike_device.cpp for exact values
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
//    data    -   value to write, in bytes, little-endian
//    len     -   number of bytes in data
//
//   return  -   size of bytes written on success; otherwise return 0

uint32_t device_write(uint8_t param, uint8_t* data, size_t len) {
  return 0;
}



// You must implement this function.
// It is called when the device receives a Device Data packet.
// Modifies data to contain the parameter value.
//    param           -   Parameter index
//    data            -   buffer to return data in, little-endian
//    len             -   length of the buffer left to write to
//
//    return          -   sizeof(param) on success; 0 otherwise 

uint8_t device_read(uint8_t param, uint8_t* data, size_t len) {
  if (len < sizeof(uint8_t)|| param > 2) {
    return 0;
  }
  float *data_float = (float *)data;
  data_float[0] = ((float) analogRead(pins[param]))/1023;
  return sizeof(float);
}

// You must implement this function.
// It is called when the BBB sends a message to the Smart Device tellinng the Smart Device to disable itself.
// Consult README.md, section 6, to see what exact functionality is expected out of disable.
void device_disable() {
//Do nothing.  This is a sensor.
}
