#include "hibike_message2.h"

message_t hibikeMessage;
uint8_t payloadArray[MAX_PAYLOAD_SIZE] = {};


uint8_t checksum(message_t* msg) {
  uint8_t chk = msg->messageID;
  int payload_length = getPayloadLength(msg);
  if (payload_length < 0) {
    // TODO: throw temper tantrum here
  }

  for (int i=0; i<payload_length; i++) {
    chk ^= msg->payload[i];
  }

  return chk;
}


int getPayloadLength(message_t* msg) {
  int payload_length;

  switch (msg->messageID) {
    case SUBSCRIPTION_REQUEST:
      payload_length = SUBSCRIPTION_REQUEST_PAYLOAD;
      break;

    case SUBSCRIPTION_RESPONSE:
      payload_length = SUBSCRIPTION_RESPONSE_PAYLOAD;
      break;

    case DATA_UPDATE:
      payload_length = DATA_UPDATE_PAYLOAD;
      break;

    default:
      payload_length = -1;
  }

  return payload_length;
}


void writeMessage(message_t* msg) {
  msg->checksum = checksum(msg);

  Serial.write(msg->messageID);
  Serial.write(msg->payload, getPayloadLength(msg));
  Serial.write(msg->checksum);
}


void readMessage(message_t* msg) {
  if (!Serial.available()) return;
  memset(msg->payload, 0, MAX_PAYLOAD_SIZE);

  messageID msgID;
  Serial.readBytes((char*) &msgID, 4);
  msg->messageID = (uint8_t) msgID;

  switch (msgID) {
    case SUBSCRIPTION_REQUEST:
      Serial.readBytes(msg->payload, );
      Serial.readBytes(&(msg->checksum), 1);
      break;

    default:
      return;
  }

  if (checksum(msg) != msg->checksum) {
    // TODO: throw temper tantrum here
  }
}