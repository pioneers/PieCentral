#ifndef HIBIKE_H
#define HIBIKE_H
#include "Arduino.h"

#define MAX_PAYLOAD_SIZE    25
#define MESSAGEID_BYTES     1
#define PAYLOAD_SIZE_BYTES  1
#define CHECKSUM_BYTES      1

#define UID_DEVICE_BYTES    2
#define UID_YEAR_BYTES      1
#define UID_ID_BYTES        8
#define UID_BYTES           UID_DEVICE_BYTES+UID_YEAR_BYTES+UID_ID_BYTES

// Enumerations
typedef enum {
  SUBSCRIPTION_REQUEST    = 0x00,
  SUBSCRIPTION_RESPONSE   = 0x01,
  DATA_UPDATE             = 0x02,
  DEVICE_UPDATE           = 0x03,
  DEVICE_STATUS           = 0x04,
  DEVICE_RESPONSE         = 0x05,
  ERROR                   = 0xFF
} messageID;

typedef enum {
  LIMIT_SWITCH = 0x01,
} deviceID;

typedef enum {
  GENERIC_ERROR   = 0xFF,
} errorID;

// Struct definitions
typedef struct hibikeMessage {
  uint8_t messageID;
  uint8_t payload_length;
  uint8_t payload[MAX_PAYLOAD_SIZE];
} message_t;

typedef struct hibike_uid {
  uint16_t device_type;
  uint8_t year;
  uint64_t id;
} hibike_uid_t;

// Function prototypes
uint8_t checksum(uint8_t* data, int length);
int send_message(message_t* msg);
int read_message(message_t* msg);
void send_subscription_response(hibike_uid_t* uid, uint16_t delay);
void data_update(message_t* msg, uint8_t* data, uint8_t payload_length);

void uid_to_byte(uint8_t* data, hibike_uid_t* uid);
uint16_t payload_to_uint16(uint8_t* payload);
void uint16_to_payload(uint16_t data, uint8_t* payload);

void message_to_byte(uint8_t* data, message_t* msg);


#endif /* HIBIKE_H */