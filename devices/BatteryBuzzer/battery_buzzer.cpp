#include "battery_buzzer.h"

uint8_t safe, connected;
float cell_voltages[NUM_CELLS], v_total;

// unbalanced for each cell is relative to the cell after it mod 3
float cell_readings[NUM_CELLS];
int cell_pins[NUM_CELLS] = {BATT_0, BATT_1, BATT_2};
cell_state cell_states[NUM_CELLS] = {CELL_SAFE, CELL_SAFE, CELL_SAFE};
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

// returns new state of a cell assuming currently safe
cell_state new_state(size_t cell) {
    if (cell_readings[cell] < CONNECTED_ENTER_THRESHOLD) {
      return CELL_DISCONNECTED;
    } else if (cell_voltages[cell] < LOW_VOLTAGE_ENTER_THRESHOLD) {
      return CELL_LOW_VOLTAGE;
    } else if (abs_diff(cell_voltages[cell], cell_voltages[(cell + 1) % NUM_CELLS]) > UNBALANCED_ENTER_THRESHOLD) {
      return CELL_UNBALANCED;
    } else {
      return CELL_SAFE;
    }
}

void read_voltage() {
  digitalWrite(READ_ENABLE_PIN, HIGH);

  // BATT_0 = 1/2 * v_0
  // BATT_1 = 1/4 * (v_0 + v_1)
  // BATT_2 = 10/61 * (v_0 + v_1 + v_2)
  size_t cell;
  for (cell = 0; cell < NUM_CELLS; cell++) {
    cell_readings[cell] = analogRead(cell_pins[cell]);
  }
  digitalWrite(READ_ENABLE_PIN, LOW);

  cell_voltages[0] = (float) cell_readings[0] * 2.0 * VOLTS_PER_UNIT;
  cell_voltages[1] = (float) cell_readings[1] * 4.0 * VOLTS_PER_UNIT - cell_voltages[0];
  cell_voltages[2] = (float) cell_readings[2] * 6.1 * VOLTS_PER_UNIT - (cell_voltages[1] + cell_voltages[0]);
  v_total = cell_voltages[0] + cell_voltages[1] + cell_voltages[2];

  // update cell_states
  for (cell = 0; cell < NUM_CELLS; cell++) {
    switch (cell_states[cell]) {
      case CELL_SAFE:
        cell_states[cell] = new_state(cell);
        break;
      case CELL_DISCONNECTED:
        if (cell_readings[cell] > DISCONNECTED_EXIT_THRESHOLD) {
          cell_states[cell] = new_state(cell);
        }
        break;
      case CELL_LOW_VOLTAGE:
        if (cell_voltages[cell] > LOW_VOLTAGE_EXIT_THRESHOLD) {
          cell_states[cell] = new_state(cell);
        }
        break;
      case CELL_UNBALANCED:
        if (abs_diff(cell_voltages[cell], cell_voltages[(cell + 1) % NUM_CELLS]) > UNBALANCED_EXIT_THRESHOLD) {
          cell_states[cell] = new_state(cell);
        }
        break;
    } 
  }
  safe = 1;
  connected = 1;
  for (cell = 0; cell < NUM_CELLS; cell++) {
    if (cell_states[cell] == CELL_DISCONNECTED) {
      connected = 0;
    }
    if (cell_states[cell] != CELL_SAFE) {
      safe = 0;
    }
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
  if (buf_len < (sizeof(safe) + sizeof(connected) + sizeof(cell_voltages) + sizeof(v_total))) {
    return 0;
  }
  uint8_t offset = 0;
  append_buf(data_update_buf, &offset, (uint8_t *)&safe, sizeof(safe));
  append_buf(data_update_buf, &offset, (uint8_t *)&connected, sizeof(connected));
  append_buf(data_update_buf, &offset, (uint8_t *)&cell_voltages, sizeof(cell_voltages));
  append_buf(data_update_buf, &offset, (uint8_t *)&v_total, sizeof(v_total));
  return offset;
}

