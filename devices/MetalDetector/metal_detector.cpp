#include "metal_detector.h"

// the last stored measurements or over 5*16 measurments
volatile bool valid = false;
uint32_t reading = 0;
uint32_t reading_offset = 0;
uint32_t history[HISTORY_LEN];  // Circular buffer
uint8_t histIndex = 0;
uint8_t measureCounter = MEASURE_EVERY-1;

// Reading1 and 2 are written by an interrupt so to avoid race conditions, the ISR will change
// either reading1 or 2 and then toggle useReading2.
uint32_t reading1 = 0;
uint32_t reading2 = 0;
bool useReading2 = false;
bool request_calibrate;
uint8_t num_calibrations = 0;

int32_t value = 0; // calibrated reading value


// normal arduino setup function, you must call hibike_setup() here
void setup() {
  // configure interrupt
  attachInterrupt(digitalPinToInterrupt(TRIG_PIN), time_oscillation, RISING);

  // configure input
  pinMode(TRIG_PIN, OUTPUT);
  digitalWrite(TRIG_PIN, LOW);
  delay(2);
  digitalWrite(TRIG_PIN, HIGH);
  delay(2);
  pinMode(TRIG_PIN, INPUT);
  digitalWrite(TRIG_PIN, LOW);

  request_calibrate = true;
  hibike_setup();
}

// normal arduino loop function, you must call hibike_loop() here
// hibike_loop will look for any packets in the serial buffer and handle them
void loop() {
  if (valid && request_calibrate) {
    calibrate();
    request_calibrate = false;
  }

  hibike_loop();
}

// Triggered once per oscillation of the metal detector
// The period increases when steel is near and decreases with aluminum
void time_oscillation() {
  if (measureCounter == 0) {
    // Take the time, update the history buffer, and update the reading
    uint32_t now = micros();
    if (useReading2) {  // Overwrite the unused of the two readings to avoid race condition
      reading1 = now - history[histIndex];
      useReading2 = false;
    } else {
      reading2 = now - history[histIndex];
      useReading2 = true;
    }
    history[histIndex] = now;
    histIndex = (histIndex+1) & HISTORY_INDEX_MASK; // cyclic incrementation
    if (histIndex == 0) {
      valid = true;
    }
    measureCounter = MEASURE_EVERY - 1;
  } else {
    measureCounter -= 1;
  }
}


void calibrate() {
  if (valid) {
    reading_offset = useReading2 ? reading1 : reading2
  }

  toggleLED();
}


int32_t get_reading() {
  if (~valid) {
    return 0;
  }

  value = (int32_t) useReading2 ? reading1 : reading2 - (int32_t) reading_offset;
}


// you must implement this function. It is called when the device receives a DeviceUpdate packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_update(uint8_t param, uint32_t value) {
  if (param == 0) {
    if (value == 1) {
      request_calibrate = true;
      return ++num_calibrations;
    }

    return num_calibrations;
  }

  return ~((uint32_t) 0);
}


uint32_t device_status(uint8_t param) {
  if (param == 0) {
    return 0;
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
  get_reading();
  append_buf(data_update_buf, &offset, (int32_t *) &value, sizeof(value));
  return offset;
}