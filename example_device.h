#include "hibike_message.h"

#ifndef EX_DEVICE_H
#define EX_DEVICE_H

// prototypes
void setup();
void loop();
uint16_t payload_to_uint16(uint8_t* payload);
void uint16_to_payload(uint16_t data, uint8_t* payload);
void toggleLED();

#endif /* EX_DEVICE_H */