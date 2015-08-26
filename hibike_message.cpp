#include "hibike_message.h"

//// CLASS METHOD IMPLEMENTATIONS //////////////////////////////////////////////

//// FUN WITH CHECKSUMS //////////////////////////////////////////////

void SubscriptionRequest::calculateChecksum() {
  if (checksumCalculated) return;
  checksum ^= (uint8_t) messageId;
  checksum ^= controllerId;
  checksum ^= subscriptionDelay & 0xFF;
  checksum ^= (subscriptionDelay >> 8) & 0xFF;
  checksum ^= (subscriptionDelay >> 16) & 0xFF;
  checksum ^= (subscriptionDelay >> 24) & 0xFF;
  checksumCalculated = true;
}

void SubscriptionResponse::calculateChecksum() {
  if (checksumCalculated) return;
  checksum ^= (uint8_t) messageId;
  checksum ^= controllerId;
  checksumCalculated = true;
}

void SensorUpdate::calculateChecksum() {
  if (checksumCalculated) return;
  checksum ^= (uint8_t) messageId;
  checksum ^= controllerId;
  checksum ^= (uint8_t) sensorTypeId;
  checksum ^= sensorReadingLength & 0xFF;
  checksum ^= (sensorReadingLength >> 8) & 0xFF;
  for (uint16_t i = 0; i < sensorReadingLength; i++) {
    checksum ^= *(dataPtr+i) & 0xFF;
  }
  checksumCalculated = true;
}

void Error::calculateChecksum() {
  if (checksumCalculated) return;
  checksum ^= (uint8_t) messageId;
  checksum ^= controllerId;
  checksum ^= (uint8_t) errorCode;
  checksumCalculated = true;
}

//// MESSAGE SENDING /////////////////////////////////////////////////

// Note: we assume that Serial (from the Arduino libraries) has already
// been imported
void SubscriptionRequest::send() {
  calculateChecksum();
  Serial.write((uint8_t) messageId);
  Serial.write(controllerId);
  Serial.write((uint8_t*) &subscriptionDelay, sizeof(uint32_t));
  Serial.write(checksum);
}

void SubscriptionResponse::send() {
  calculateChecksum();
  Serial.write((uint8_t) messageId);
  Serial.write(controllerId);
  Serial.write(checksum);
}

void SensorUpdate::send() {
  calculateChecksum();
  Serial.write((uint8_t) messageId);
  Serial.write(controllerId);

  Serial.write((uint8_t) sensorTypeId);
  Serial.write((uint8_t*) &sensorReadingLength, sizeof(uint16_t));
  Serial.write(dataPtr, (size_t) sensorReadingLength);

  Serial.write(checksum);
}

void Error::send() {
  calculateChecksum();
  Serial.write((uint8_t) messageId);
  Serial.write(controllerId);
  Serial.write((uint8_t) errorCode);
  Serial.write(checksum);
}

//// MESSAGE RECEIVING /////////////////////////////////////////////////////////
//
// Receives an incoming hibike message.
// Returns a null pointer if no data is on the serial port.
//
// Note that Arduino's Serial.readBytes function automatically
// waits until either the given number of bytes are successfully
// read or a timeout occurs (defaults to 1000ms, but this is an
// eternity for our use case so we should probably change this to a
// few ms at most).
//
HibikeMessage* receiveHibikeMessage() {
  if (!Serial.available()) {
    return nullptr;
  }
  //TODO: implement better error checking to detect/deal with possible failures
  HibikeMessageType messageId;
  uint8_t controllerId, checksum;
  HibikeMessage *m;
  Serial.readBytes((char*) &messageId, 1);
  Serial.readBytes((char*) &controllerId, 1);
  switch (messageId) {
    case HibikeMessageType::SubscriptionRequest:
      uint32_t subscriptionDelay;
      Serial.readBytes((char*) &subscriptionDelay, 4);
      m = new SubscriptionRequest(controllerId, subscriptionDelay);
      break;
    case HibikeMessageType::Error:
      // TODO: add proper error handling dependant on errorCode
      ErrorCode errorCode;
      Serial.readBytes((char*) &errorCode, 1);
      m = new Error(controllerId, errorCode);
      break;
    default:
      // TODO: implement missing message types
      Error(controllerId, ErrorCode::InvalidMessageType).send();
  }
  Serial.readBytes((char*) &checksum, 1);
  if (checksum ^ m->getChecksum()) {
    // send an error back to the main controller if the checksums aren't identical
    Error(controllerId, ErrorCode::ChecksumMismatch).send();
  }
  return m;
}
