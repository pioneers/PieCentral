#include "color_sensor.h"


tcs34725IntegrationTime_t it = DEFAULT_INTEGRATION_TIME;
tcs34725Gain_t gain = DEFAULT_GAIN;
Adafruit_TCS34725 tcs;
volatile uint32_t toggle = 1; // 0 means LED light off, 1 means on

// normal arduino setup function, you must call hibike_setup() here
void setup() {
  tcs = Adafruit_TCS34725(it, gain);
  pinMode(TOGGLE_PIN, OUTPUT);
  hibike_setup();
}

// normal arduino loop function, you must call hibike_loop() here
// hibike_loop will look for any packets in the serial buffer and handle them
void loop() {

  // do whatever you want here
  // note that hibike will only process one packet per call to hibike_loop()
  // so exessive delays here will affect hibike.

  hibike_loop();
}


// you must implement this function. It is called when the device receives a DeviceUpdate packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_update(uint8_t param, uint32_t value) {

  switch (param) {

    case INTEGRATION_TIME:
      it = (tcs34725IntegrationTime_t) (value & 0xFF);
      tcs.setIntegrationTime(it);
      return it;
      break;

    case GAIN:
      gain = (tcs34725Gain_t) (value & 0xFF);
      tcs.setGain(gain);
      return gain;
      break;

    case TOGGLE:
      toggle = value;
      if (toggle == 1) {
        digitalWrite(TOGGLE_PIN, HIGH);
      } else if (toggle == 0) {
        digitalWrite(TOGGLE_PIN, LOW);
      }
      return toggle;
      break;

    default:
      return ~((uint32_t) 0);


  }
}

// you must implement this function. It is called when the devie receives a DeviceStatus packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_status(uint8_t param) {

  switch (param) {

    case INTEGRATION_TIME:
      return it;
      break;

    case GAIN:
      return gain;
      break;

    case TOGGLE:
      return toggle;
      break;

    default:
      return ~((uint32_t) 0);


  }
}


// you must implement this function. It is called with a buffer and a maximum buffer size.
// The buffer should be filled with appropriate data for a DataUpdate packer, and the number of bytes
// added to the buffer should be returned. 
//
// You can use the helper function append_buf.
// append_buf copies the specified amount data into the dst buffer and increments the offset
uint8_t data_update(uint8_t* data_update_buf, size_t buf_len) {
  if (buf_len < sizeof(uint16_t) * 4) {
    return 0;
  }
  uint16_t *rgbc = (uint16_t *) data_update_buf;

  // this function will delay for whatever we set the integration time to ASSUMINGS ITS A VALID tcs34725IntegrationTime_t
  // because the library hardcoded delays with a switch statement instead of calculating them from the integration time...
  tcs.getRawData(&rgbc[0], &rgbc[1], &rgbc[2], &rgbc[3]);

  return sizeof(uint16_t) * 4;
}

// You must implement this function.
// It is called when the BBB sends a message to the Smart Device tellinng the Smart Device to disable itself.
// Consult README.md, section 6, to see what exact functionality is expected out of disable.
void device_disable() {

}
