#include "hibike_message.h"

//// CLASS METHOD IMPLEMENTATIONS /////////////////////////////////////////////

//// FUN WITH CHECKSUMS ///////////////////////////////////////////////
uint8_t HibikeMessage::getChecksum() {
  if (!checksumCalculated) {
    checksum = calculateChecksum()
  }
  return checksum;
}

void SubscriptionRequest::calculateChecksum() {
  uint8_t cs = 0;
  cs ^= messageId;
  cs ^= controllerId;
  cs ^= subscriptionDelay & 0xFF;
  cs ^= (subscriptionDelay >> 8) & 0xFF;
  cs ^= (subscriptionDelay >> 16) & 0xFF;
  cs ^= (subscriptionDelay >> 24) & 0xFF;
  checksum = cs;
  checksumCalculated = true;
}

void SubscriptionResponse::calculateChecksum() {
  uint8_t cs = 0;
  cs ^= messageId;
  cs ^= controllerId;
  cs ^= errorCode;
  checksum = cs;
  checksumCalculated = true;
}

void SubscriptionSensorUpdate::calculateChecksum() {
  uint8_t cs = 0;
  cs ^= messageId;
  cs ^= controllerId;
  cs ^= sensorTypeId;
  cs ^= sensorReadingLength & 0xFF
  cs ^= (sensorReadingLength >> 8) & 0xFF
  for (int i = 0; i < sensorReadingLength; i++) {
    cs ^= *(dataPtr+i) & 0xFF;
  }
  checksum = cs;
  checksumCalculated = true;
}

void Error::calculateChecksum() {
  uint8_t cs = 0;
  cs ^= messageId;
  cs ^= controllerId;
  cs ^= errorCode
  checksum = cs;
  checksumCalculated = true;
}

//// MESSAGE SENDING //////////////////////////////////////////////////
void SubscriptionRequest::send() {
}
void SubscriptionResponse::send() {
}
void SubscriptionSensorUpdate::send() {
}
void Error::send() {
}

//
// Receives an incoming hibike message.
// Returns a null pointer if no data is on the serial port.
//
// Note that Arduino's Serial.readBytes function automatically
// waits until either the given number of bytes are successfully
// read or a timeout occurs (defaults to 1000ms).
//
HibikeMessage* receiveHibikeMessage() {
  if (!Serial.available()) {
    return NULL;
  }
}
