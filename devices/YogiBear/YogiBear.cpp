#include "YogiBear.h"

// each device is responsible for keeping track of it's own params
uint32_t params[NUM_PARAMS];

/*
  YOGI BEAR PARAMS:
    duty = percent duty cycle
    fault : {1 = normal operation, 0 = fault}
    forward : {1 = forward, 0 = reverse}
    inputA : {1 = High, 0 = Low}
    inputB : {1 = High, 0 = Low}
*/

uint32_t duty;
uint32_t fault;
uint32_t forward;
uint32_t inputA;
uint32_t inputB;

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
  // value1++;
  //   value2++;
  //   value3++;
  //   value4++;

  hibike_loop();
}


// you must implement this function. It is called when the device receives a DeviceUpdate packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
/* 
    DUTY
    EN/DIS
    FORWARD/REVERSE
    FAULT LINE

    future:
    ENCODER VALUES -library?
    PID mode vs Open Loop modes; PID Arduino library
    Current Sense - loop update Limit the PWM if above the current for current motor
*/
uint32_t device_update(uint8_t param, uint32_t value) {
  // if (param < NUM_PARAMS) {
  //     params[param] = value;
  //     return params[param];
  //   }
  
  switch (param) {

    case DUTY:
      if (value <= 100) && (value >= 0) {
        duty = value;
      }
      return duty;
      break;
      
    case FORWARD:
      forward = 1;
      inputA = 0;
      inputB = 1;
      return forward;
      break;

    case REVERSE:
      forward = 0;
      inputA = 1;
      inputB = 0;
      return forward;
      break;

    default:
      return ~((uint32_t) 0);
  }
}

// you must implement this function. It is called when the device receives a DeviceStatus packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_status(uint8_t param) {
  // if (param < NUM_PARAMS) {
  //   return params[param];
  // }
  switch (param) {
    case DUTY:
      return duty;
      break;
      
    case FAULT:
      return fault;
      break;
      
    case FORWARD:
      return forward;
      break;
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
  return offset;
}

