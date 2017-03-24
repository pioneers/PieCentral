#include "hibike_message.h"



uint8_t hid_recv_buffer[COBS_DELIM_BYTES+COBS_LENGTH_BYTES+MAX_PAYLOAD_SIZE+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+CHECKSUM_BYTES+COBS_OVERHEAD_BYTES];

void hibike_message_setup() {
  #ifdef HIBIKE_HID_MODE
  RawHID.begin(hid_recv_buffer, sizeof(hid_recv_buffer));
  #else
  Serial.begin(115200);
  #endif
}

int hibike_message_available() {
  #ifdef HIBIKE_HID_MODE
  return RawHID.available();
  #else
  return Serial.available();
  #endif
}

uint8_t checksum(uint8_t data[], int length) {
  uint8_t chk = data[0];
  for (int i=1; i<length; i++) {
    chk ^= data[i];
  }
  return chk;
}

#ifdef HIBIKE_HID_MODE
int send_message_hid(message_t *msg) {
  uint8_t data[MAX_PAYLOAD_SIZE+ MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+CHECKSUM_BYTES];
  // TODO karthik-shanmugam: check buffer size
  uint8_t cobs_buf[COBS_DELIM_BYTES+COBS_LENGTH_BYTES+MAX_PAYLOAD_SIZE+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+CHECKSUM_BYTES+COBS_OVERHEAD_BYTES];
  message_to_byte(data, msg);
  data[msg->payload_length+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES] = checksum(data, msg->payload_length+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES);

  // cobs encoding, leading 0 to signal start of packet and then a length byte
  cobs_buf[0] = 0x00;
  size_t cobs_len = cobs_encode(&cobs_buf[2], data, msg->payload_length+ MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+CHECKSUM_BYTES);
  


  cobs_buf[1] = (byte) cobs_len;
  size_t written = RawHID.write(cobs_buf, 2 + cobs_len);
  if (written != 2 + cobs_len) {
    return -1;
  }
  return 0;
}
#else
int send_message_serial(message_t *msg) {
  uint8_t data[MAX_PAYLOAD_SIZE+ MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+CHECKSUM_BYTES];
  // TODO karthik-shanmugam: check buffer size
  uint8_t cobs_buf[COBS_DELIM_BYTES+COBS_LENGTH_BYTES+MAX_PAYLOAD_SIZE+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+CHECKSUM_BYTES+COBS_OVERHEAD_BYTES];
  message_to_byte(data, msg);
  data[msg->payload_length+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES] = checksum(data, msg->payload_length+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES);
  
  // cobs encoding, leading 0 to signal start of packet and then a length byte
  cobs_buf[0] = 0x00;
  size_t cobs_len = cobs_encode(&cobs_buf[2], data, msg->payload_length+ MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+CHECKSUM_BYTES);
  cobs_buf[1] = (byte) cobs_len;
  uint8_t written = Serial.write(cobs_buf, 2 + cobs_len);
  if (written != 2 + cobs_len) {
    return -1;
  }
  return 0;
}
#endif

#ifdef HIBIKE_HID_MODE
// reads everything available on hid and returns -1
// convenience function for read_message_hid
int hid_clear() {
  size_t hid_len = RawHID.available();
  for (int i=0;i<hid_len;i++){RawHID.read();}
  return -1;
}
// TODO karthik-shanmugam : debug this and investigate if we can use it
// this is supposed to be a function that reads directly from the RawHID buffer
// currently the other function, read_message_hid_stream, which uses RawHID's byte-stream-like API, is the one used
int read_message_hid(message_t *msg) {
  uint8_t data[MAX_PAYLOAD_SIZE+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES];
  size_t hid_len = RawHID.available();
  if (hid_len < 2) return hid_clear();
  if (hid_recv_buffer[0] != 0) return hid_clear();
  size_t cobs_len = hid_recv_buffer[1];
  if (hid_len < cobs_len + 2) return hid_clear();
  if (cobs_decode(data, hid_recv_buffer, cobs_len) < 3) return hid_clear();

  // we're done with the hid_recv_buffer at this point
  hid_clear();
  uint8_t messageID = data[0];
  uint8_t payload_length = data[1];
  uint8_t expected_chk = checksum(data, payload_length+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES);
  uint8_t received_chk = data[MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+payload_length];

  if (received_chk != expected_chk) {
    return -1;
  }
  msg->messageID = messageID;
  msg->payload_length = payload_length;
  memcpy(msg->payload, &data[MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES], payload_length);
  return 0;
}

// simulates the behaviour of Serial.readBytesUntil()
size_t raw_hid_read_bytes_until(uint8_t term, uint8_t* buf, size_t len) {
  size_t read = 0;
  for (int i = 0; i < len; i++) {
    while(RawHID.available() == 0){}
    if (RawHID.peek() == term) break;
    buf[i] = RawHID.read();
    read++;
  }
  return read;
}

// nearly a 1:1 copy of the serial version of this function
// potentially suboptimal because HID is packet-based but this uses a byte stream API
int read_message_hid_stream(message_t *msg) {
  uint8_t data[MAX_PAYLOAD_SIZE+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+CHECKSUM_BYTES];
  // TODO karthik-shanmugam: check buffer size
  uint8_t cobs_buf[COBS_DELIM_BYTES+COBS_LENGTH_BYTES+MAX_PAYLOAD_SIZE+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+CHECKSUM_BYTES+COBS_OVERHEAD_BYTES];

  // find the start of packet
  int last_byte_read = -1;
  while (RawHID.available()) {
    last_byte_read = RawHID.read();
    if (last_byte_read == 0) {
      break;
    }
  }

  // no start of packet found
  if (last_byte_read != 0) {
    return -1;
  }

  // no packet length found
  if (RawHID.available() == 0 || RawHID.peek() == 0) {
    return -1;
  }
  size_t cobs_len = RawHID.read();
  size_t read_len = raw_hid_read_bytes_until(0x00, (char *)cobs_buf, cobs_len);
  if (cobs_len != read_len || cobs_decode(data, cobs_buf, cobs_len) < 3) {

    return -1;
  }
  uint8_t messageID = data[0];
  uint8_t payload_length = data[1];
  uint8_t expected_chk = checksum(data, payload_length+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES);
  uint8_t received_chk = data[MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+payload_length];
  
  // no need to empty the buffer with cobs
  if (received_chk != expected_chk) {
    return -1;
  }
  msg->messageID = messageID;
  msg->payload_length = payload_length;
  memcpy(msg->payload, &data[MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES], payload_length);
  return 0;
}
#else
int read_message_serial(message_t *msg) {
  uint8_t data[MAX_PAYLOAD_SIZE+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+CHECKSUM_BYTES];
  // TODO karthik-shanmugam: check buffer size
  uint8_t cobs_buf[COBS_DELIM_BYTES+COBS_LENGTH_BYTES+MAX_PAYLOAD_SIZE+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+CHECKSUM_BYTES+COBS_OVERHEAD_BYTES];

  // find the start of packet
  int last_byte_read = -1;
  while (Serial.available()) {
    last_byte_read = Serial.read();
    if (last_byte_read == 0) {
      break;
    }
  }

  // no start of packet found
  if (last_byte_read != 0) {
    return -1;
  }

  // no packet length found
  if (Serial.available() == 0 || Serial.peek() == 0) {
    return -1;
  }
  size_t cobs_len = Serial.read();
  size_t read_len = Serial.readBytesUntil(0x00, (char *)cobs_buf, cobs_len);
  if (cobs_len != read_len || cobs_decode(data, cobs_buf, cobs_len) < 3) {

    return -1;
  }
  uint8_t messageID = data[0];
  uint8_t payload_length = data[1];
  uint8_t expected_chk = checksum(data, payload_length+MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES);
  uint8_t received_chk = data[MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES+payload_length];
  
  // no need to empty the buffer with cobs
  if (received_chk != expected_chk) {
    return -1;
  }
  msg->messageID = messageID;
  msg->payload_length = payload_length;
  memcpy(msg->payload, &data[MESSAGEID_BYTES+PAYLOAD_SIZE_BYTES], payload_length);
  return 0;

}
#endif

int send_message(message_t* msg) {
  #ifdef HIBIKE_HID_MODE
  return send_message_hid(msg);
  #else
  return send_message_serial(msg);
  #endif
}

int read_message(message_t* msg) {
  #ifdef HIBIKE_HID_MODE
  return read_message_hid_stream(msg);
  #else
  return read_message_serial(msg);
  #endif
}

int send_heartbeat_response(uint8_t id) { // id = for future heartbeat identification
  message_t msg;
  msg.messageID = HEART_BEAT_RESPONSE;
  msg.payload_length = 0;
  int status = append_payload(&msg, id, sizeof(id));

  if(status != 0){
    return -1;
  }
  return send_message(&msg);
}

int send_heartbeat_request(uint8_t id) { // id = future hearbeat identification
  message_t msg;
  msg.messageID = HEART_BEAT_REQUEST;
  msg.payload_length = 0;
  int status = append_payload(&msg, id, sizeof(id));

  if(status != 0){
    return -1;
  }
  return send_message(&msg);
}

int send_subscription_response(uint16_t params, uint16_t delay, hibike_uid_t* uid) {
  message_t msg;
  msg.messageID = SUBSCRIPTION_RESPONSE;
  msg.payload_length = 0;

  int status = append_payload(&msg, (uint8_t*) &params, sizeof(params));
  
  status += append_payload(&msg, (uint8_t*) &delay, sizeof(delay));
  
  status += append_payload(&msg, (uint8_t*) &uid->device_type, UID_DEVICE_BYTES);
  status += append_payload(&msg, (uint8_t*) &uid->year, UID_YEAR_BYTES);
  status += append_payload(&msg, (uint8_t*) &uid->id, UID_ID_BYTES);


  if (status != 0) {
    return -1;
  }
  return send_message(&msg); 
}

int send_data_update(uint16_t params) { 
  message_t msg;
  msg.messageID = DEVICE_DATA;
  msg.payload_length = 2;

  // iterate over the params bitmap
  for (uint16_t count = 0; (params >> count) > 0; count++) {

      // check if a particular bit is set
      if (params & (1<<count)){
        int bytes_written = device_read((uint8_t) count, &msg.payload[msg.payload_length], (size_t) sizeof(msg.payload) - msg.payload_length);
        if(bytes_written){
          msg.payload_length += bytes_written;
        }

        // if we failed to write anything for a param, make sure its bit is unset
        else{
          params &= ~(1<<count);
        }
      }
  }

  *((uint16_t *) &msg.payload[0]) = params;

  if (msg.payload_length > MAX_PAYLOAD_SIZE) {
    return -1;
  } else {
    return send_message(&msg);
  }
}

int send_error_packet(uint8_t error_code) {
  message_t msg;
  msg.messageID = ERROR;
  msg.payload_length = 0;

  int status = append_payload(&msg, (uint8_t*) &error_code, sizeof(error_code));

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

void append_buf(uint8_t* buf, uint8_t* offset, uint8_t* data, uint8_t length) {
  memcpy(&(buf[*offset]), data, length);
  *offset += length;
}


void uid_to_byte(uint8_t* data, hibike_uid_t* uid) {
  data[0] = (uint8_t) (uid->device_type & 0xFF);
  data[1] = (uint8_t) (uid->device_type >> 8);
  data[2] = uid->year;
  for (size_t i = 0; i < sizeof(uid->id); i++) {
    data[3 + i] = (uint8_t) ((uid->id >> (8 * i)) & 0xFF);
  }
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
