#include "servo_control.h"

Servo servos[NUM_PINS];

/*uint64_t prevTime, currTime, heartbeat;
uint8_t param, servo;
uint32_t value;
uint16_t subDelay;
bool led_enabled;
*/

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

// you must implement this function. It is called when the device receives a DeviceUpdate packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_write(uint8_t param, uint8_t* value, size_t len) {
  if(param< NUM_PINS && len< sizeof(servos[param]) || len< sizeof(toggle0)){
    return 0;
  }

  if (param < NUM_PINS) {
    servos[param].write((value[0]);
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

    // case TOGGLE2:
    //   toggle2 = value[0];
    //   return sizeof(toggle_servo(2, toggle2));
    //   break;

    // case TOGGLE3:
    //   toggle3 = value[0];
    //   return sizeof(toggle_servo(3, toggle3));
    //   break;

    default:
      return 0;
  }
}

uint32_t toggle_servo(int servo_num, uint32_t toggle) {
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

// you must implement this function. It is called when the deviCe receives a DeviceStatus packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_status(uint8_t param) {
  if (param < NUM_PINS) {
    return servos[param].read();
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

uint8_t device_data_update(int param, uint8_t* data_update_buf, size_t buf_len) {
  if(MAX_PAYLOAD_SIZE - buf_len < sizeof(uint8_t)|| param>NUM_PINS*2 || param < 0){
    return 0;
  }
  if(param<2){
    data_update_buf[0] = ((uint8_t)servos[param].read()); //32 bit return, must cast to 8 bit buffer
  }
  else if (params == NUM_PINS){
    data_update_buf[0] = toggle0;
  }
  else if (params == NUM_PINS+1){
    data_update_buf[0] = toggle1;
  }
  
  return sizeof(uint8_t);
}