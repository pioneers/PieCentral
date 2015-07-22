#include "hibike_message.h"
#include "Arduino.h"
#include "assert.h"

//
// The controller_id of this hibike endpoint.
//
uint8_t controller_id;

//
// helper function declarations. see function definitions for
// more documentation
//
void send_message(*hibike_message_t);
uint8_t calculate_checksum(*hibike_message_t);

//
// the rx buffer. max message limit of
// 256 bytes was chosen more or less
// arbitrarily
//
uint8_t rx_buffer[256] = {0};

//
// the amount of time to wait in between sending SUBSCRIPTION_SENSOR_UPDATEs
//
uint32_t delay_time = 0;


//
// Initializes this hibike endpoint, setting its controller_id to
// my_controller_id. Aside from this, the function is really just a
// glorified wrapper for Arduino serial setup.
//
void hibike_init(uint8_t my_controller_id) {
  controller_id = my_controller_id;
  Serial.begin(57600); // baud rate arbitrarily chosen for now. may change
}

//
// Sends a subscription response to the beaglebone controller.
//
void send_subscription_response(uint8_t error_code) {
  hibike_message_t m;
  m.message_id = HIBIKE_MESSAGE.SUBSCRIPTION_RESPONSE;
  m.controller_id = controller_id;
  m.payload.error_code = error_code;
  send_message(&m);
}

//
// Sends a subscription sensor update to the beaglebone controller.
//
void send_subscription_sensor_update(uint8_t sensor_type_id, uint16_t len, uint8_t *data) {
  hibike_message_t m;
  m.message_id = HIBIKE_MESSAGE.SUBSCRIPTION_SENSOR_UPDATE;
  m.controller_id = controller_id;
  m.payload.sensor_data.sensor_type_id = sensor_type_id;
  m.payload.sensor_data.sensor_reading_length = len;
  m.payload.sensor_data.data = data;
  send_message(&m);
}

//
// Sends a hibike error message with the given error code
// to the other hibike endpoint.
//
void send_error(uint8_t error_code) {
  hibike_message_t m;
  m.message_id = HIBIKE_MESSAGE.ERROR;
  m.controller_id = controller_id;
  m.payload.error_code = error_code;
  send_message(&m);
}

//
// Receives an incoming hibike message.
// Note that the pointer returned points to the rx_buffer.
// Returns a null pointer if no data is on the serial port.
//
// Note that Arduino's Serial.readBytes function automatically
// waits until either the given number of bytes are successfully
// read or a timeout occurs (defaults to 1000ms).
//
hibike_message_t* receive_message() {
  if (!Serial.available()) {
    return nullptr;
  }
  hibike_message_t *m = (*hibike_message_t) rx_buffer;
  Serial.readBytes(&m->message_id, sizeof(uint8_t));
  Serial.readBytes(&m->controller_id, sizeof(uint8_t));
  switch(m->message_id) {
    //
    // these message types are either currently unsupported
    // or should never be sent to this type of endpoint. In
    // either case, send back an error.
    //
    case HIBIKE_MESSAGE.SUBSCRIPTION_RESPONSE:
    case HIBIKE_MESSAGE.SUBSCRIPTION_SENSOR_UPDATE:
    case HIBIKE_MESSAGE.SENSOR_UPDATE:
    case HIBIKE_MESSAGE.SENSOR_UPDATE_REQUEST:
      send_error(ERROR.INVALID_MESSAGE_TYPE);
      break;
    case HIBIKE_MESSAGE.SUBSCRIPTION_REQUEST:
      Serial.readBytes(&m->payload.delay, sizeof(uint32_t));
      break;
    case HIBIKE_MESSAGE.ERROR:
      Serial.readBytes(&m->payload.error_code, sizeof(uint8_t));
      break;
  }
  Serial.readBytes(&m->checksum, sizeof(uint8_t));
  uint8_t checksum = calculate_checksum(m);
  if (checksum != m->checksum) {
    send_error(ERROR.CHECKSUM_MISMATCH);
  }
}

//
// Calculates and sets the checksum for the given hibike_message
//
void calculate_checksum(hibike_message_t *m) {
  uint8_t checksum = 0;
  checksum ^= m->message_id;
  checksum ^= m->controller_id;
  switch(m->message_id) {
    //
    // like above, have no need to consider these message types at
    // this time.
    //
    case HIBIKE_MESSAGE.SUBSCRIPTION_RESPONSE:
    case HIBIKE_MESSAGE.SUBSCRIPTION_SENSOR_UPDATE:
    case HIBIKE_MESSAGE.SENSOR_UPDATE:
    case HIBIKE_MESSAGE.SENSOR_UPDATE_REQUEST:
      break;
    case HIBIKE_MESSAGE.SUBSCRIPTION_RESPONSE:
    case HIBIKE_MESSAGE.ERROR:
      checksum ^= m->payload.error_code;
      break;
    case HIBIKE_MESSAGE.SUBSCRIPTION_SENSOR_UPDATE:
      checksum ^= m->payload.sensor_data.sensor_type_id;
      checksum ^= m->payload.sensor_data.sensor_reading_length & 0xFF;
      checksum ^= (m->payload.sensor_data.sensor_reading_length >> 4) & 0xFF;
      uint8_t len = m->payload.sensor_data.sensor_reading_length;
      uint8_t *data = m->payload.sensor_data.data;
      for (int i = 0; i < len; i++) {
        checksum ^= *(data+i);
      }
      break;
  }
  m->checksum = checksum
}

//
// Sends the given hibike message over serial to the other
// hibike endpoint. The standard use case of this will be to
// send messages from arduino->beaglebone.
//
// We could definitely make calculate_checksum/send_message
// more efficient by doing both at the same time, but I'm currently
// too lazy to implement this.
// TODO(vincent): get this optimization done eventually.
void send_message(hibike_message_t *m) {
  calculate_checksum(message);
  Serial.write(&m->message_id, sizeof(uint8_t));
  Serial.write(&m->controller_id, sizeof(uint8_t));
  switch(m->message_id) {
    //
    // once again non-require message types.
    //
    case HIBIKE_MESSAGE.SUBSCRIPTION_RESPONSE:
    case HIBIKE_MESSAGE.SUBSCRIPTION_SENSOR_UPDATE:
    case HIBIKE_MESSAGE.SENSOR_UPDATE:
    case HIBIKE_MESSAGE.SENSOR_UPDATE_REQUEST:
      break;
    case HIBIKE_MESSAGE.SUBSCRIPTION_RESPONSE:
    case HIBIKE_MESSAGE.ERROR:
      Serial.write(&m->payload.error_code, sizeof(uint8_t));
      break;
    case HIBIKE_MESSAGE.SUBSCRIPTION_SENSOR_UPDATE:
      Serial.write(&m->payload.sensor_data.sensor_type_id, sizeof(uint8_t));
      uint16_t len = m->payload.sensor_data.sensor_reading_length;
      Serial.write(&len, sizeof(uint16_t));
      Serial.write(m->payload.sensor_data.data, len);
      break;
  }
  Serial.write(&m->checksum, sizeof(uint8_t));
}
