#ifndef HIBIKE_H
#define HIBIKE_H
#include "Arduino.h"

#define MAX_PAYLOAD_SIZE 12

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
#define SUBSCRIPTION_REQUEST_PAYLOAD 1
#define SUBSCRIPTION_RESPONSE_PAYLOAD 12
#define DATA_UPDATE_PAYLOAD 1

typedef enum {
    LIMIT_SWITCH    = 0x01,
} deviceID

typedef enum {
    GENERIC_ERROR   = 0xFF,
} errorID

// Struct definitions
struct hibikeMessage {
    uint8_t  messageID;
    uint8_t* payload;
    uint8_t  checksum;
} message_t;

// Function prototypes
uint8_t checksum(message_t*);
int getPayloadLength(message_t*);
void writeMessage(message_t*);
void readMessage(message_t*);

#endif /* HIBIKE_H */