#ifndef HIBIKE_H
#define HIBIKE_H
#include "Arduino.h"
#include "devices.h"
#include "cobs.h"

#define MAX_PAYLOAD_SIZE    100
#define MESSAGEID_BYTES     1
#define PAYLOAD_SIZE_BYTES  1
#define CHECKSUM_BYTES      1

#define MAX_FRAGMENT_SIZE   (MAX_PAYLOAD_SIZE - 1)

#define UID_DEVICE_BYTES    2
#define UID_YEAR_BYTES      1
#define UID_ID_BYTES        8
#define UID_BYTES           (UID_DEVICE_BYTES+UID_YEAR_BYTES+UID_ID_BYTES)

#define DEVICE_PARAM_BYTES   1
#define DEVICE_VALUE_BYTES   4
#define DEVICE_BYTES         (DEVICE_PARAM_BYTES+DEVICE_VALUE_BYTES)

// Enumerations
typedef enum {
  PING                    = 0x10,
  SUBSCRIPTION_REQUEST    = 0x11,
  SUBSCRIPTION_RESPONSE   = 0x12,
  DEVICE_READ             = 0x13,
  DEVICE_WRITE            = 0x14,
  DEVICE_DATA             = 0x15,
  DEVICE_DISABLE          = 0x16,
  HEART_BEAT_REQUEST      = 0x17,
  HEART_BEAT_RESPONSE     = 0x18,

  ERROR                   = 0xFF,
} messageID;

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

int send_heartbeat_response(uint8_t id);
int send_heartbeat_request(uint8_t id);
int send_subscription_response(uint16_t params, uint16_t delay, hibike_uid_t* uid);
int send_data_update(uint16_t params);
int send_error_packet(uint8_t error_code);
int append_payload(message_t* msg, uint8_t* data, uint8_t length);
void append_buf(uint8_t* buf, uint8_t* offset, uint8_t* data, uint8_t length);

uint8_t uint8_from_message(message_t* msg, uint8_t* offset);
uint16_t uint16_from_message(message_t* msg, uint8_t* offset);
uint32_t uint32_from_message(message_t* msg, uint8_t* offset);
uint64_t uint64_from_message(message_t* msg, uint8_t* offset);

void message_to_byte(uint8_t* data, message_t* msg);

extern uint8_t device_read(uint8_t param, uint8_t* data, size_t len);

#endif /* HIBIKE_H */
