#include "YogiBear.h"

// each device is responsible for keeping track of it's own params

/*
  YOGI BEAR PARAMS:
    duty = percent duty cycle
    fault : {1 = normal operation, 0 = fault}
    forward : {1 = forward, 0 = reverse}
    inputA : {1 = High, 0 = Low}
    inputB : {1 = High, 0 = Low}
*/

/*
   These variables have nothing to do with the
   json file other than the fact that they have the
   same name, but these could have been named anything.
   They are simply dummy variables for hibike to interface with.
   The realization of the control is reflected in the arduino
   code.
*/
uint32_t duty;
uint32_t fault;
uint32_t forward;
uint32_t inputA;
uint32_t inputB;

int INA = 4;
int INB = 7;
int PWM = 9;
int EN = IO4;

// int IN_ENA = I08;
// int IN_ENB = IO9;
volatile unsigned int encoder0Pos = 0; 
//might need to process or not make unsigned

// normal arduino setup function, you must call hibike_setup() here
void setup() {
  hibike_setup();
  pinMode(INA, OUTPUT);
  pinMode(INB, OUTPUT);
  pinMode(PWM, OUTPUT);
  // pinMode(IN_ENA, INPUT); 
  // digitalWrite(IN_ENA, HIGH);
  // pinMode(IN_ENB, INPUT); 
  // digitalWrite(IN_ENB, HIGH);
  digitalWrite(INA, LOW);
  digitalWrite(INB, HIGH);
  // attachInterrupt(0, doEncoder, CHANGE);
}

// normal arduino loop function, you must call hibike_loop() here
// hibike_loop will look for any packets in the serial buffer and handle them
void loop() {
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
      if ((value <= 100) && (value >= 0)) {
        duty = value;
        int scaled255 = value * (255/100);
        analogWrite(PWM, scaled255);
      }
      return duty;
      break;
      
    case FORWARD:
      forward = 1;
      inputA = 0;
      inputB = 1;
      digitalWrite(INA, LOW);
      digitalWrite(INB, HIGH);
      return forward;
      break;

    case REVERSE:
      forward = 0;
      inputA = 1;
      inputB = 0;
      digitalWrite(INA, HIGH);
      digitalWrite(INB, LOW);
      return forward;
      break;

    case FAULT:
      if (fault == 0){
          // clearFault();
          return fault;
      } else {
          return fault;
      }

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

    case REVERSE:
      return !forward;
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



uint32_t device_write(uint8_t param, uint8_t* data, size_t len){
  uint8_t value;
  switch (param) {
    case PARAM_DUTY:
      value = data[0];
      if ((value <= 100) && (value >= 0)) {
        duty = value;
        int scaled255 = value * (255/100);
        analogWrite(PWM, scaled255);
      }
      return sizeof(uint8_t);
      break;
    case PARAM_FORWARD:
      value = data[0];
      forward = value;
      if (forward) {
        forward = 1;
        inputA = 0;
        inputB = 1;
        digitalWrite(INA, LOW);
        digitalWrite(INB, HIGH);
      } else {
        forward = 0;
        inputA = 1;
        inputB = 0;
        digitalWrite(INA, HIGH);
        digitalWrite(INB, LOW);
      }
      return sizeof(uint8_t);
      break;
  }
  return 0;
}


// you must implement this function. It is called with a buffer and a maximum buffer size.
// The buffer should be filled with appropriate data for a DataUpdate packer, and the number of bytes
// added to the buffer should be returned. 
//
// You can use the helper function append_buf.
// append_buf copies the specified amount data into the dst buffer and increments the offset


uint8_t device_data_update(int param, uint8_t* data_update_buf, size_t buf_len) {

  switch (param) {
    case PARAM_DUTY:
      data_update_buf[0] = duty;
      return sizeof(uint8_t);
      break;
    case PARAM_FORWARD:
      data_update_buf[0] = forward;
      return sizeof(uint8_t);
      break;
  }
  return 0;

}