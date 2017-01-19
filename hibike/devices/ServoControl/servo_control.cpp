#include "servo_control.h"

Servo servos[NUM_PINS];

uint8_t pins[NUM_PINS] = {SERVO_0, SERVO_1};

volatile uint8_t toggle0 = 1; // 0 means servo off, 1 means on
volatile uint8_t toggle1 = 1; 

void setup() {
  hibike_setup();

  // Setup sensor input
  for (int i = 0; i < NUM_PINS; i++) {
    servos[i].attach(pins[i]);
  }
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

uint32_t device_write(uint8_t param, uint8_t* value, size_t len) {
  if(param< NUM_PINS && len< sizeof(servos[param]) || len< sizeof(toggle0)){
    return 0;
  }

  if (param < NUM_PINS) {
    servos[param].write(value[0]);
    return sizeof(value[0]);
  }

  switch (param) {

    case TOGGLE0:
      toggle0 = value[0];
      return sizeof(toggle_servo(0, toggle0));
      break;

    case TOGGLE1:
      toggle1 = value[0];
      return sizeof(toggle_servo(1, toggle1));
      break;

    default:
      return 0;
  }
}


uint8_t toggle_servo(int servo_num, uint8_t toggle) {
  if ((toggle == 1) && (!servos[servo_num].attached())) {
    servos[servo_num].attach(pins[servo_num]);
  } else if ((toggle == 0) && (servos[servo_num].attached())) {
    servos[servo_num].detach();
  }
  else{
    return 0;
  }
  return toggle;
}


// You must implement this function.
// It is called when the device receives a Device Data Update packet.
// Modifies data_update_buf to contain the parameter value.
//    param           -   Parameter index
//    data_update_buf -   buffer to return data in
//    buf_len         -   Maximum length of the buffer? TODO: Clarify
//
//    return          -   sizeof(param) on success; 0 otherwise

uint8_t device_data_update(uint8_t param, uint8_t* data_update_buf, size_t buf_len) {
  if (MAX_PAYLOAD_SIZE - buf_len < sizeof(uint8_t) ||
      param > NUM_PINS * 2) {
    return 0;
  }
  if (param<2) {
    data_update_buf[0] = ((uint8_t)servos[param].read()); //32 bit return, must cast to 8 bit buffer
  }
  else if (param == NUM_PINS) {
    data_update_buf[0] = toggle0;
  }
  else if (param == NUM_PINS + 1) {
    data_update_buf[0] = toggle1;
  }
  
  return sizeof(uint8_t);
}
