#ifndef HIBIKE_H
#define HIBIKE_H

/**
 * Message IDs for each type of hibike message.
 */
enum HIBIKE_MESSAGE {
  SUBSCRIPTION_REQUEST,
  SUBSCRIPTION_RESPONSE,
  SUBSCRIPTION_SENSOR_UPDATE,
  SENSOR_UPDATE_REQUEST,
  SENSOR_UPDATE,
  ERROR = 0xFF,
};

/**
 * Subscription Response status codes.
 */ enum SUBSCRIPTION_RESPONSE { SUCCESS,
  GENERIC_ERROR = 0xFF,
};

/**
 * Sensor Type IDs
 */
enum SENSOR_TYPE {
};

/**
 * More specific error codes.
 */
enum ERROR {
  INVALID_MESSAGE_TYPE = 0xFB,
  MALFORMED_MESSAGE = 0xFC,
  INVALID_ARDUINO_ID = 0xFD,
  CHECKSUM_MISMATCH = 0xFE,
  GENERIC_ERROR = 0xFF,
};

typedef struct {
  uint8_t message_id;
  uint8_t controller_id;
  union payload {
    uint32_t delay; // for use with MESSAGE_TYPE.SUBSCRIPTION_REQUEST
    struct sensor_data {
      uint8_t sensor_type_id;
      uint16_t sensor_reading_length;
      uint8_t *data;
    };
    uint8_t error_code; // for use with MESSAGE_TYPE.SUBSCRIPTION_RESPONSE || MESSAGE_TYPE.ERROR
  }
  uint8_t checksum;
} hibike_message_t;


//
// the amount of time to wait in between SUBSCRIPTION_SENSOR_UPDATEs
//
extern uint32_t update_delay_time;

void hibike_init();

//
// TODO: The three commented out functions below would be nice to have but aren't
//       strictly required. Finish implementing them eventually.
//
////////////////////////////// Message sending //////////////////////////////
/* void send_subscription_request(uint32_t); */
void send_subscription_response(uint8_t);
void send_subscription_sensor_update(uint8_t, uint16_t, *uint8_t);
/* void send_sensor_update_request(); */
/* void send_sensor_update(uint8_t, uint16_t, *uint8_t); */
void send_error(uint8_t);

///////////////////////////// Message receiving /////////////////////////////
hibike_message_t* receive_message();

#endif /* HIBIKE_H */
