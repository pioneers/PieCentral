#ifndef INC_HIBIKE_DEVICE
#define INC_HIBIKE_DEVICE

#include "hibike_message.h"
#include "devices.h"
#include "util.h"
#include <stdint.h>
// For size_t
#include <string.h>

typedef enum {
  RESTING,
  FIRST_BEAT,
  BREAK,
  SECOND_BEAT
} led_state;

// Analog Input Pins
#define IO0 A0
#define IO1 A1
#define IO2 A2
#define IO3 A3

// Digital Input Pins
#define IO4 2
#define IO5 3
#define IO6 6
#define IO7 9
#define IO8 10
#define IO9 11

#define LED_PIN 13

extern hibike_uid_t UID;
void hibike_setup(uint32_t _disable_latency, uint32_t _heartbeatDelay);
void hibike_setup(); //calls hibike_setup(args) with default values.
void hibike_loop();
void toggleLED();

// these are implimented in the device's .cpp files.
extern uint32_t device_write(uint8_t param, uint8_t* data, size_t len);
extern uint8_t device_read(uint8_t param, uint8_t* data, size_t len);
extern void device_disable();


#endif  // INC_HIBIKE_DEVICE
