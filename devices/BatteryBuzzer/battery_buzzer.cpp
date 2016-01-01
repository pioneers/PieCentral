#include "battery_buzzer.h"

uint8_t safe, connected;
uint16_t v0, v1, v2;
// normal arduino setup function, you must call hibike_setup() here
void setup() {
  pinMode(CELL_0, INPUT_PULLUP);
  pinMode(CELL_1, INPUT_PULLUP);
  pinMode(CELL_2, INPUT_PULLUP);
  pinMode(READ_ENABLE_PIN, OUTPUT);
  read_voltage();
  hibike_setup();
}

// normal arduino loop function, you must call hibike_loop() here
// hibike_loop will look for any packets in the serial buffer and handle them
void loop() {
  read_voltage();
  if (safe) {
    noTone(BUZZER_PIN);
  } else {
    tone(BUZZER_PIN, BUZZER_FREQ);
  }
  hibike_loop();
}

void read_voltage() {
  digitalWrite(READ_ENABLE_PIN, HIGH);
  uint16_t cell_0 = analogRead(CELL_0);
  uint16_t cell_1 = analogRead(CELL_1);
  uint16_t cell_2 = analogRead(CELL_2);
  digitalWrite(READ_ENABLE_PIN, LOW);
  v0 = cell_0 * 2;
  v1 = cell_1 * 4 - v0;
  v2 = cell_2 * 6 - v1;

  if (v0 < CONNECTED_THRESHOLD || v1 < CONNECTED_THRESHOLD || v2 < CONNECTED_THRESHOLD) {
    connected = 0;
    safe = 0;
  }  else if (v0 < SAFE_THRESHOLD || v1 < SAFE_THRESHOLD || v2 < SAFE_THRESHOLD) {
    connected = 1;
    safe = 0;
  } else if (abs_diff(v0, v1) < BALANCE_THRESHOLD 
          || abs_diff(v1, v2) < BALANCE_THRESHOLD 
          || abs_diff(v2, v0) < BALANCE_THRESHOLD) {
    connected = 1;
    safe = 0;
  } else {
    connected = 1;
    safe = 1;
  }
}

uint16_t abs_diff(uint16_t a, uint16_t b) {
  if (a > b) {
    return a - b;
  } else {
    return b - a;
  }
}

// you must implement this function. It is called when the device receives a DeviceUpdate packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_update(uint8_t param, uint32_t value) {
  return ~((uint32_t) 0);
}

// you must implement this function. It is called when the devie receives a DeviceStatus packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_status(uint8_t param) {
  return ~((uint32_t) 0);
}


// you must implement this function. It is called with a buffer and a maximum buffer size.
// The buffer should be filled with appropriate data for a DataUpdate packer, and the number of bytes
// added to the buffer should be returned. 
//
// You can use the helper function append_buf.
// append_buf copies the specified amount data into the dst buffer and increments the offset
uint8_t data_update(uint8_t* data_update_buf, size_t buf_len) {
  if (buf_len < (sizeof(safe) + sizeof(connected) + sizeof(v0) + sizeof(v1) + sizeof(v2))) {
    return 0;
  }
  uint8_t offset = 0;
  append_buf(data_update_buf, &offset, (uint8_t *)&safe, sizeof(safe));
  append_buf(data_update_buf, &offset, (uint8_t *)&connected, sizeof(connected));
  append_buf(data_update_buf, &offset, (uint8_t *)&v0, sizeof(v0));
  append_buf(data_update_buf, &offset, (uint8_t *)&v1, sizeof(v1));
  append_buf(data_update_buf, &offset, (uint8_t *)&v2, sizeof(v2));
  return offset;
}

