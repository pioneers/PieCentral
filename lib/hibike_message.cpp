#include "hibike_message.h"

//// CLASS METHOD IMPLEMENTATIONS //////////////////////////////////////////////

//// FUN WITH CHECKSUMS //////////////////////////////////////////////
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

//// MESSAGE SENDING /////////////////////////////////////////////////

// Note: we assume that Serial (from the Arduino libraries) has already
// been imported
void SubscriptionRequest::send() {
  Serial.write(messageId);
  Serial.write(controllerId);
  Serial.write((uint8_t*) &subscriptionDelay, sizeof(uint32_t));
  Serial.write(checksum);
}

void SubscriptionResponse::send() {
  Serial.write(messageId);
  Serial.write(controllerId);
  Serial.write(checksum);
}

void SubscriptionSensorUpdate::send() {
  Serial.write(messageId);
  Serial.write(controllerId);

  Serial.write(sensorTypeId);
  Serial.write((uint8_t*) &sensorReadingLength, sizeof(uint16_t));
  Serial.write(dataPtr, (size_t) sensorReadingLength);

  Serial.write(checksum);
}

void Error::send() {
  Serial.write(messageId);
  Serial.write(controllerId);
  Serial.write(errorCode);
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
std::unique_ptr<HibikeMessage> receiveHibikeMessage() {
  if (!Serial.available()) {
    return nullptr;
  }
  //TODO: implement better error checking to detect/deal with possible failures
  uint8_t messageId, controllerId, checksum;
  HibikeMessage m;
  Serial.readBytes(&messageId, 1);
  Serial.readBytes(&controllerId, 1);
  switch (messageId) {
    case HibikeMessageType.SubscriptionRequest:
      uint32_t subscriptionDelay;
      Serial.readBytes(&subscriptionDelay, 4);
      m = new SubscriptionRequest(controllerId, subscriptionDelay);
      break;
    case Error:
      // TODO: add proper error handling dependant on errorCode
      uint8_t errorCode;
      Serial.readBytes(&errorCode, 1);
      m = new Error(controllerId, errorCode);
      break;
    default:
      // TODO: implement missing message types
      Error(controllerId, ErrorCode.InvalidMessageType).send();
  }
  Serial.readBytes(&checksum, 1);
  if (checksum ^ m.getChecksum()) {
    // send an error back to the main controller if the checksums aren't identical
    Error(controllerId, ErrorCode.ChecksumMismatch).send();
  }
  return unique_ptr<HibikeMessage>(m);
}
