#ifndef HIBIKE_H
#define HIBIKE_H
#include "Arduino.h"

// Enumerations
typedef enum {
    SUBCRIPTION_REQUEST     = 0x01,
    SUBSCRIPTION_RESPONSE   = 0x02,
    DATA_UPDATE             = 0x03,
    DEVICE_UPDATE           = 0x04,
    DEVICE_STATUS           = 0x05,
    DEVICE_RESPONSE         = 0x06,
    ERROR                   = 0xFF
} messageID

// TODO: fill out the rest of these enumerations
// TODO: find a clean way to enumerate payload length;
//       should be easier on the device side
typedef enum {
    LIMIT_SWITCH    = 0x01,
} deviceType

typedef enum {
    GENERIC_ERROR   = 0xFF,
}

// Struct definitions
struct hibikeMessage {
    uint8_t messageID;
    uint8_t payload;
    uint8_t checksum;
} message_t;

// Function prototypes
uint8_t checksum(message_t*);
void send(message_t*);
message_t* readPort(void);
uint8_t readSensor(void);

#endif /* HIBIKE_H */