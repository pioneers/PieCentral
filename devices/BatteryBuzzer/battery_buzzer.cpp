#include "battery_buzzer.h"

uint8_t safe, connected;
float v_0, v_1, v_2, v_total;

// normal arduino setup function, you must call hibike_setup() here
void setup() {
  pinMode(BATT_0, INPUT);
  pinMode(BATT_1, INPUT);
  pinMode(BATT_2, INPUT);
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

  // BATT_0 = 1/2 * v_0
  // BATT_1 = 1/4 * (v_0 + v_1)
  // BATT_2 = 10/61 * (v_0 + v_1 + v_2)
  uint16_t in0 = analogRead(BATT_0);
  uint16_t in1 = analogRead(BATT_1);
  uint16_t in2 = analogRead(BATT_2);
  v_0 = (float) in0 * 2.0 * VOLTS_PER_UNIT;
  v_1 = (float) in1 * 4.0 * VOLTS_PER_UNIT - v_0;
  v_2 = (float) in2 * 6.1 * VOLTS_PER_UNIT - (v_1 + v_0);
  v_total = v_0 + v_1 + v_2;
  digitalWrite(READ_ENABLE_PIN, LOW);


  // battery is disconnected and therefor unsafe if all inputs are low. This works on raw input values
  if (in0 < CONNECTED_THRESHOLD && in1 < CONNECTED_THRESHOLD && in2 < CONNECTED_THRESHOLD) {
    connected = 0;
    safe = 0;

  // battery is unsafe if the voltage drops too low
  }  else if (v_0 < SAFE_THRESHOLD || v_1 < SAFE_THRESHOLD || v_2 < SAFE_THRESHOLD) {
    connected = 1;
    safe = 0;

  // battery is also unsafe if two cells have a large voltage difference
  } else if (abs_diff(v_0, v_1) > BALANCE_THRESHOLD 
          || abs_diff(v_1, v_2) > BALANCE_THRESHOLD 
          || abs_diff(v_2, v_0) > BALANCE_THRESHOLD) {
    connected = 1;
    safe = 0;
  } else {
    connected = 1;
    safe = 1;
  }
}

float abs_diff(float a, float b) {
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
  if (buf_len < (sizeof(safe) + sizeof(connected) + sizeof(v_0) + sizeof(v_1) + sizeof(v_2))) {
    return 0;
  }
  uint8_t offset = 0;
  append_buf(data_update_buf, &offset, (uint8_t *)&safe, sizeof(safe));
  append_buf(data_update_buf, &offset, (uint8_t *)&connected, sizeof(connected));
  append_buf(data_update_buf, &offset, (uint8_t *)&v_0, sizeof(v_0));
  append_buf(data_update_buf, &offset, (uint8_t *)&v_1, sizeof(v_1));
  append_buf(data_update_buf, &offset, (uint8_t *)&v_2, sizeof(v_2));
  append_buf(data_update_buf, &offset, (uint8_t *)&v_total, sizeof(v_total));
  return offset;
}

