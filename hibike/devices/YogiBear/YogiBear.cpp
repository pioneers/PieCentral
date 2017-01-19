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
  digitalWrite(INA, LOW);
  digitalWrite(INB, HIGH);
}

// normal arduino loop function, you must call hibike_loop() here
// hibike_loop will look for any packets in the serial buffer and handle them
void loop() {
  hibike_loop();
}


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

// You must implement this function.
// It is called when the device receives a Device Write packet.
// Updates param to new value passed in data.
//    param   -   Parameter index
//    data    -   value to write, in little-endian bytes
//    len     -   number of bytes in data
//
//   return  -   size of bytes written on success; otherwise return 0

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
