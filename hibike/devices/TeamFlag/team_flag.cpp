#include "team_flag.h"

const uint8_t pins[NUM_PINS] = {BLUE, YELLOW, LED1, LED2, LED3, LED4};
uint8_t led_values[NUM_PINS] = {0, 0, 0, 0, 0, 0};
void setup() {
  hibike_setup();
  // Setup sensor input
  for (int i = 0; i < NUM_PINS; i++) {
    digitalWrite(pins[i], LOW);
    pinMode(pins[i], OUTPUT);
  }
}


void loop() {
  hibike_loop();
}

uint8_t data_update(uint8_t* data_update_buf, size_t buf_len) {
  uint8_t offset = 0;
  return offset;
}


void setLed(uint8_t pin, uint16_t value) {
  digitalWrite(pins[pin], value);
  led_values[pin] = value;
}


uint8_t getLed(uint8_t pin) {
  return led_values[pin];
}

uint32_t device_write(uint8_t param, uint8_t* data, size_t len){
  switch (param) {
    case PARAM_BLUE:
      setLed(0, data[0]);
      return sizeof(uint8_t);
      break;
    case PARAM_YELLOW:
      setLed(1, data[0]);
      return sizeof(uint8_t);
      break;
    case PARAM_LED1:
      setLed(2, data[0]);
      return sizeof(uint8_t);
      break;
    case PARAM_LED2:
      setLed(3, data[0]);
      return sizeof(uint8_t);
      break;
    case PARAM_LED3:
      setLed(4, data[0]);
      return sizeof(uint8_t);
      break;
    case PARAM_LED4:
      setLed(5, data[0]);
      return sizeof(uint8_t);
      break;
    default:
      break;
  }
  return 0;
}

uint8_t device_data_update(int param, uint8_t* data_update_buf, size_t buf_len) {
  switch (param) {
    case PARAM_BLUE:
      data_update_buf[0] = getLed(0);
      return sizeof(uint8_t);
      break;
    case PARAM_YELLOW:
      data_update_buf[0] = getLed(1);
      return sizeof(uint8_t);
      break;
    case PARAM_LED1:
      data_update_buf[0] = getLed(2);
      return sizeof(uint8_t);
      break;
    case PARAM_LED2:
      data_update_buf[0] = getLed(3);
      return sizeof(uint8_t);
      break;
    case PARAM_LED3:
      data_update_buf[0] = getLed(4);
      return sizeof(uint8_t);
      break;
    case PARAM_LED4:
      data_update_buf[0] = getLed(5);
      return sizeof(uint8_t);
      break;
    default:
      break;
  }
  return 0;
}