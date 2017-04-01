#include "team_flag.h"

const uint8_t pins[NUM_PINS] = {BLUE, YELLOW, LED1, LED2, LED3, LED4};
uint8_t led_values[NUM_PINS] = {0, 0, 0, 0, 0, 0};


void setup() {
  hibike_setup(); //use default heartbeat rates. look at /lib/hibike/hibike_device.cpp for exact values
  // Setup sensor input
  for (int i = 0; i < NUM_PINS; i++) {
    digitalWrite(pins[i], LOW);
    pinMode(pins[i], OUTPUT);
  }
}


void loop() {
  hibike_loop();
}


void setLed(uint8_t pin, uint16_t value) {
  digitalWrite(pins[pin], value);
  led_values[pin] = value;
}


uint8_t getLed(uint8_t pin) {
  return led_values[pin];
}


// You must implement this function.
// It is called when the device receives a Device Write packet.
// Updates param to new value passed in data.
//    param   -   Parameter index
//    data    -   value to write, in bytes TODO: What endian?
//    len     -   number of bytes in data
//
//   return  -   size of bytes written on success; otherwise return 0

uint32_t device_write(uint8_t param, uint8_t* data, size_t len){
  if (len < sizeof(uint8_t)) {
    return 0;
  }
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


// You must implement this function.
// It is called when the device receives a Device Data Update packet.
// Modifies data to contain the parameter value.
//    param           -   Parameter index
//    data -   buffer to return data in
//    len         -   Maximum length of the buffer? TODO: Clarify
//
//    return          -   sizeof(param) on success; 0 otherwise

uint8_t device_read(uint8_t param, uint8_t* data, size_t len) {
  if (len < sizeof(uint8_t)) {
    return 0;
  }
  switch (param) {
    case PARAM_BLUE:
      data[0] = getLed(0);
      return sizeof(uint8_t);
      break;
    case PARAM_YELLOW:
      data[0] = getLed(1);
      return sizeof(uint8_t);
      break;
    case PARAM_LED1:
      data[0] = getLed(2);
      return sizeof(uint8_t);
      break;
    case PARAM_LED2:
      data[0] = getLed(3);
      return sizeof(uint8_t);
      break;
    case PARAM_LED3:
      data[0] = getLed(4);
      return sizeof(uint8_t);
      break;
    case PARAM_LED4:
      data[0] = getLed(5);
      return sizeof(uint8_t);
      break;
    default:
      break;
  }
  return 0;
}

// You must implement this function.
// It is called when the BBB sends a message to the Smart Device tellinng the Smart Device to disable itself.
// Consult README.md, section 6, to see what exact functionality is expected out of disable.
void device_disable() {

}
