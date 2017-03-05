#include "metal_detector.h"

volatile bool valid = false;  // False until the history buffer fills and the reading is valid
uint32_t history[HISTORY_LEN];  // Circular buffer
uint8_t histIndex = 0;
uint8_t measureCounter = MEASURE_EVERY-1;

// Reading1 and 2 are written by an interrupt so to avoid race conditions, the ISR will change
// either reading1 or 2 and then toggle useReading2.
uint32_t reading1 = 0;
uint32_t reading2 = 0;
bool useReading2 = false;
uint32_t calibrate_val = 0;

void setup() {

  initIsr();
  initDetector();
  hibike_setup();
}


void loop() {

  hibike_loop();
}

uint32_t getReading() {

  return useReading2 ? reading2 : reading1;
}

void initDetector() {

  pinMode(TRIG_PIN, OUTPUT);
  digitalWrite(TRIG_PIN, LOW);
  delay(2);
  digitalWrite(TRIG_PIN, HIGH);
  delay(2);
  pinMode(TRIG_PIN, INPUT);
  digitalWrite(TRIG_PIN, LOW);
}

void initIsr() {

  cli();  // Disable interrupts while changing settings
  // Configure trigger on falling edge
  EICRA = (EICRA & ~((1 << ISC00) | (1 << ISC01))) | (1 << ISC01) | (0 << ISC00);
  EIFR &= ~_BV(INTF0);  // Clear any previous triggers
  EIMSK |= _BV(INT0);  // Enable INT1 interrupt vector
  sei();  // Enable interrupts
}

// Triggered once per oscillation of the metal detector
// The period increases when steel is near and decreases with aluminum
ISR(INT0_vect) {

  if (measureCounter == 0) {
    // Take the time, update the history buffer, and update the reading
    uint32_t now = micros();
    if (useReading2) {  // Overwrite the unused of the two readings to avoid race condition
      reading1 = now - history[histIndex];
      useReading2 = false;
    }else {
      reading2 = now - history[histIndex];
      useReading2 = true;
    }
    history[histIndex] = now;
    histIndex = (histIndex+1) & HISTORY_INDEX_MASK;
    if (histIndex == 0) {
      valid = true;
    }
    measureCounter = MEASURE_EVERY - 1;
  }else {
    measureCounter -= 1;
  }
}

uint32_t device_update(uint8_t param, uint32_t value) {

  if (param == 0) {
    calibrate_val = getReading();
    return value;
  }

  return ~((uint32_t) 0);
}

uint32_t device_status(uint8_t param) {
  if (param == 0) {
    return calibrate_val;
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
  
  int32_t reading = getReading() - calibrate_val;
  uint8_t offset = 0;
  append_buf(data_update_buf, &offset, (uint8_t *)&reading, sizeof(reading));
  return offset;
}

// You must implement this function.
// It is called when the BBB sends a message to the Smart Device tellinng the Smart Device to disable itself.
// Consult README.md, section 6, to see what exact functionality is expected out of disable.
void device_disable() {

}
