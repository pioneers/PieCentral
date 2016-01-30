#include "servo_control.h"

Servo servos[NUM_PINS];

/*uint64_t prevTime, currTime, heartbeat;
uint8_t param, servo;
uint32_t value;
uint16_t subDelay;
bool led_enabled;
*/

uint8_t pins[NUM_PINS] = {SERVO_0, SERVO_1, SERVO_2, SERVO_3};

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
uint32_t device_update(uint8_t param, uint32_t value) {
  if (param < NUM_PINS) {
    servos[param].write(value);
    return servos[param].read();
  }
  return ~((uint32_t) 0);
}

// you must implement this function. It is called when the devie receives a DeviceStatus packet.
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