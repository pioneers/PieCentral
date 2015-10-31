#include "hibike_message.h"

uint8_t checksum(uint8_t data[], int length) {
  uint8_t chk = data[0];
  for (int i=1; i<length; i++) {
    chk ^= data[i];
  }
  return chk;
}


int send_message(message_t *msg) {
  uint8_t data[msg->payload_length+ MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+CHECKSUM_BYTES];
  message_to_byte(data, msg);
  data[msg->payload_length+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES] = checksum(data, msg->payload_length+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES);
  uint8_t written = Serial.write(data, msg->payload_length+ MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+CHECKSUM_BYTES);
  if (written != msg->payload_length+ MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+CHECKSUM_BYTES) {
    return -1;
  }
  return 0;
}


// Returns 0 on success, -1 on error (ex. no message)
// If checksum does not match, empties the incoming buffer. 
int read_message(message_t *msg) {
  if (!Serial.available()) {
    return -1;
  }

  uint8_t data[MAX_PAYLOAD_SIZE+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES]; 
  Serial.readBytes((char*) data, MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES);
  uint8_t length = data[MESSAGEID_BYTES];
  Serial.readBytes((char*) data+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES, length);

  uint8_t chk = checksum(data, length+
    MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES);
  int expected_chk_ind = MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+length;
  Serial.readBytes((char*) data+expected_chk_ind, 1);

  if (chk != data[expected_chk_ind]) {
    // Empty incoming buffer
    while (Serial.available() > 0) {
      Serial.read();
    }
    return -1;
  }

  msg->messageID = data[0];
  msg->payload_length = data[MESSAGEID_BYTES];
  for (int i = 0; i < length; i++){
    msg->payload[i] = data[i+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES];
  }

  return 0;
}

int send_subscription_response(hibike_uid_t* uid, uint16_t delay) {
  message_t msg;
  msg.messageID = SUBSCRIPTION_RESPONSE;
  msg.payload_length = 0;

  int status = 0;
  status += append_payload(&msg, (uint8_t*) &uid->device_type, UID_DEVICE_BYTES);
  status += append_payload(&msg, (uint8_t*) &uid->year, UID_YEAR_BYTES);
  status += append_payload(&msg, (uint8_t*) &uid->id, UID_ID_BYTES);

  status += append_payload(&msg, (uint8_t*) &delay, sizeof(delay));

  if (status != 0) {
    return -1;
  }
  return send_message(&msg); 
}


int send_data_update(uint8_t* data, uint8_t payload_length) {
  message_t msg;
  msg.messageID = DATA_UPDATE;
  msg.payload_length = 0;
  int status = append_payload(&msg, data, payload_length);
  
  if (status != 0) {
    return -1;
  }
  return send_message(&msg); 
}


int send_device_response(uint8_t param, uint32_t value) {
  message_t msg;
  msg.messageID = DEVICE_RESPONSE;
  msg.payload_length = 0;

  int status = 0;
  status += append_payload(&msg, &param, DEVICE_PARAM_BYTES);
  status += append_payload(&msg, (uint8_t*) &value, DEVICE_VALUE_BYTES);

  if (status != 0) {
    return -1;
  }
  return send_message(&msg);
}




int append_payload(message_t* msg, uint8_t* data, uint8_t length) {
  memcpy(&(msg->payload[msg->payload_length]), data, length);
  msg->payload_length += length;
  if (msg->payload_length > MAX_PAYLOAD_SIZE) {
    return -1;
  }
  return 0;
}


void uid_to_byte(uint8_t* data, hibike_uid_t* uid) {
  data[0] = (uint8_t) (uid->device_type & 0xFF);
  data[1] = (uint8_t) (uid->device_type >> 8);
  data[2] = uid->year;
  for (size_t i = 0; i < sizeof(uid->id); i++) {
    data[3 + i] = (uint8_t) ((uid->id >> (8 * i)) & 0xFF);
  }
}

void device_update(message_t* msg, uint8_t param, uint32_t value) {
  msg->messageID = DEVICE_UPDATE;
  msg->payload_length = 0;
  uint8_to_message(msg, param);
  uint32_to_message(msg, value);

}
void device_status(message_t* msg, uint8_t param, uint32_t value) {
  msg->messageID = DEVICE_STATUS;
  msg->payload_length = 0;
  uint8_to_message(msg, param);
  uint32_to_message(msg, value);
}
void device_response(message_t* msg, uint8_t param, uint32_t value) {
  msg->messageID = DEVICE_RESPONSE;
  msg->payload_length = 0;
  uint8_to_message(msg, param);
  uint32_to_message(msg, value);
}
void error_message(message_t* msg, uint8_t error_code) {
  msg->messageID = ERROR;
  msg->payload_length = 0;
  uint8_to_message(msg, error_code); 
}





// TODO decide whether to use these methods or the ones that deal with messages

// Assumes payload is little endian
uint16_t payload_to_uint16(uint8_t* payload) {
  return ((uint16_t) payload[0]) + (((uint16_t) payload[1]) << 8);
}
// Assumes payload is little endian
void uint16_to_payload(uint16_t data, uint8_t* payload) {
  payload[0] = (uint8_t) (data & 0xFF);
  payload[1] = (uint8_t) (data >> 8);
}
// Assumes payload is little endian
uint16_t payload_to_uint32(uint8_t* payload) {
  return ((uint16_t) payload[0]) + (((uint16_t) payload[1]) << 8);
}


// these functions add to the message payload and increment the payload length
void uint8_to_message(message_t* msg, uint8_t data) {
  msg->payload[msg->payload_length] = data;
  msg->payload_length += sizeof(data);
}
void uint16_to_message(message_t* msg, uint16_t data) {
  msg->payload[msg->payload_length + 0] = (uint8_t) (data & 0xFF);
  msg->payload[msg->payload_length + 1] = (uint8_t) ((data >> 8) & 0xFF);
  msg->payload_length += sizeof(data);
}
void uint32_to_message(message_t* msg, uint32_t data) {
  msg->payload[msg->payload_length + 0] = (uint8_t) (data & 0xFF);
  msg->payload[msg->payload_length + 1] = (uint8_t) ((data >> 8) & 0xFF);
  msg->payload[msg->payload_length + 2] = (uint8_t) ((data >> 16) & 0xFF);
  msg->payload[msg->payload_length + 3] = (uint8_t) ((data >> 24) & 0xFF);
  msg->payload_length += sizeof(data);
}
// what's a for loop?
void uint64_to_message(message_t* msg, uint64_t data) {
  msg->payload[msg->payload_length + 0] = (uint8_t) (data & 0xFF);
  msg->payload[msg->payload_length + 1] = (uint8_t) ((data >> 8) & 0xFF);
  msg->payload[msg->payload_length + 2] = (uint8_t) ((data >> 16) & 0xFF);
  msg->payload[msg->payload_length + 3] = (uint8_t) ((data >> 24) & 0xFF);
  msg->payload[msg->payload_length + 4] = (uint8_t) ((data >> 32) & 0xFF);
  msg->payload[msg->payload_length + 5] = (uint8_t) ((data >> 40) & 0xFF);
  msg->payload[msg->payload_length + 6] = (uint8_t) ((data >> 48) & 0xFF);
  msg->payload[msg->payload_length + 7] = (uint8_t) ((data >> 56) & 0xFF);
  msg->payload_length += sizeof(data); 
}
void uid_to_message(message_t* msg, hibike_uid_t* uid) {
  uint16_to_message(msg, uid->device_type);
  uint8_to_message(msg, uid->year);
  uint64_to_message(msg, uid->id);
}

uint8_t uint8_from_message(message_t* msg, uint8_t* offset) {
  uint8_t res = msg->payload[*offset];
  *offset += sizeof(res);
  return res;
}
uint16_t uint16_from_message(message_t* msg, uint8_t* offset) {
  uint16_t res = (msg->payload[*offset + 0] & 0xFF) << 0;
  res |= (msg->payload[*offset + 1] & 0xFF) << 8;
  *offset += sizeof(res);
  return res;
}
uint32_t uint32_from_message(message_t* msg, uint8_t* offset) {
  uint32_t res = (msg->payload[*offset + 0] & 0xFF) << 0;
  res |= (msg->payload[*offset + 1] & 0xFF) << 8;
  res |= (msg->payload[*offset + 2] & 0xFF) << 16;
  res |= (msg->payload[*offset + 3] & 0xFF) << 24;
  *offset += sizeof(res);
  return res;
}
uint64_t uint64_from_message(message_t* msg, uint8_t* offset) {
  uint64_t res = (msg->payload[*offset + 0] & 0xFF) << 0;
  res |= (msg->payload[*offset + 1] & 0xFF) << 8;
  res |= (msg->payload[*offset + 2] & 0xFF) << 16;
  res |= (msg->payload[*offset + 3] & 0xFF) << 24;
  res |= (msg->payload[*offset + 4] & 0xFF) << 32;
  res |= (msg->payload[*offset + 5] & 0xFF) << 40;
  res |= (msg->payload[*offset + 6] & 0xFF) << 48;
  res |= (msg->payload[*offset + 7] & 0xFF) << 56;
  *offset += sizeof(res);
  return res;  
}

void message_to_byte(uint8_t *data, message_t *msg) {
  data[0] = msg->messageID;
  data[1] = msg->payload_length;
  for (int i = 0; i < msg->payload_length; i++){
    data[i+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES] = msg->payload[i];
  }
}

void param_value_to_byte(uint8_t *data, uint8_t param, uint32_t value) {
  memcpy(data, &param, DEVICE_PARAM_BYTES);
  memcpy(data+DEVICE_PARAM_BYTES, &value, DEVICE_VALUE_BYTES);
}
