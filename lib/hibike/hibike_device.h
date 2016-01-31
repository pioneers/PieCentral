#ifndef INC_HIBIKE_DEVICE
#define INC_HIBIKE_DEVICE

#include "hibike_message.h"
#include "devices.h"
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
void hibike_setup();
void hibike_loop();
void toggleLED();

extern uint32_t device_update(uint8_t param, uint32_t value); 

extern uint32_t device_status(uint8_t param); 

extern uint8_t data_update(uint8_t* data_update_buf, size_t buf_len);



#endif  // INC_HIBIKE_DEVICE