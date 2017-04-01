#include "servo_control.h"

Servo servo0;
Servo servo1;
Servo servos[NUM_PINS] = {servo0, servo1};
uint8_t pins[NUM_PINS] = {SERVO_0, SERVO_1};
float positions[NUM_PINS] = {0,0};


void setup() {
  hibike_setup(); //use default heartbeat rates. look at /lib/hibike/hibike_device.cpp for exact values
  disableAll();
}

void disableAll() {
  for (int i = 0; i < NUM_PINS; i++) {
    servos[i].detach();
  }
}

void enable(int num) {
  servos[num].attach(pins[num]);
}

void loop() {
  hibike_loop();
}

// You must implement this function.
// It is called when the device receives a Device Write packet.
// Updates param to new value passed in data.
//    param   -   Parameter index
//    data    -   value to write, in bytes TODO: What endian?
//    len     -   number of bytes in data
//
//   return  -   size of bytes written on success; otherwise return 0
uint32_t device_write(uint8_t param, uint8_t* data, size_t len) {
  float value = ((float *)data)[0];
  if (value < -1 || value > 1) {
    return sizeof(float);
  }
  enable(param);
  positions[param] = value;
  servos[param].writeMicroseconds(SERVO_CENTER + (positions[param] * SERVO_RANGE/2));
  return sizeof(float); 
}

// You must implement this function.
// It is called when the device receives a Device Data Update packet.
// Modifies data to contain the parameter value.
//    param           -   Parameter index
//    data -   buffer to return data in
//    len         -   Maximum length of the buffer? TODO: Clarify
//
//    return          -   sizeof(param) on success; 0 otherwise
uint8_t device_read(uint8_t param, uint8_t* data_update_buf, size_t buf_len) {
  if(buf_len < sizeof(float)) {
    return 0;
  }
  float* float_buf = (float *) data_update_buf;
  float_buf[0] = positions[param];
  return sizeof(float);
}

// You must implement this function.
// It is called when the BBB sends a message to the Smart Device tellinng the Smart Device to disable itself.
// Consult README.md, section 6, to see what exact functionality is expected out of disable.
void device_disable() {
  disableAll();
}
