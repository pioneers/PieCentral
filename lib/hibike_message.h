#ifndef HIBIKE_H
#define HIBIKE_H
#include "Arduino.h"
#include "assert.h"
#include <memory>

enum class HibikeMessageType {
  SubscriptionRequest,
  SubscriptionResponse,
  SubscriptionSensorUpdate,
  Error = 0xFF,
}

enum class SensorType {
  LimitSwitch,
  LineFollower,
}

enum class ErrorCode {
  InvalidMessageType = 0xFB,
  MalformedMessage = 0xFC,
  InvalidArduinoId = 0xFD,
  ChecksumMismatch = 0xFE,
  GenericError = 0xFF,
}

//// CLASS DEFINITIONS //////////////////////////////////////////////////////
class HibikeMessage
{
  private:
    uint8_t messageId;
    uint8_t controllerId;
    uint8_t checksum;
    bool checksumCalculated;
    virtual void calculateChecksum() = 0;

  public:
    HibikeMessage(uint8_t mId, uint8_t cId):
      messageId(mId),
      controllerId(cId),
      checksum(0),
      checksumCalculated(false) {}

    // getter functions. We want to ensure that HibikeMessages cannot be further altered
    // after construction, and thus we choose to have the class fields private and their
    // values accessible using getters. Note that depending
    uint8_t getMessageId() { return messageId; }
    uint8_t getControllerId() { return controllerId; }
    uint8_t getChecksum() { calculateChecksum(); return checksum; }
    virtual void send() = 0;
};

class SubscriptionRequest : public HibikeMessage
{
  private:
    uint32_t subscriptionDelay;

  public:
    SubscriptionRequest(uint8_t cId, uint32_t sd):
      HibikeMessage(HibikeMessageType.SubscriptionRequest, cId),
      subscriptionDelay(sd) {}

    uint32_t getSubscriptionDelay() { return subscriptionDelay; }
};

class SubscriptionResponse : public HibikeMessage
{
  public:
    SubscriptionResponse(uint8_t cId):
      HibikeMessage(HibikeMessageType.SubscriptionResponse, cId) {}
};

class SubscriptionSensorUpdate : public HibikeMessage
{
  private:
    uint8_t sensorTypeId;
    uint16_t sensorReadingLength;
    uint8_t *dataPtr;

  public:
    SubscriptionSensorUpdate(uint8_t cId, uint8_t sId, uint16_t srl, uint8_t *p):
      HibikeMessage(HibikeMessageType.SubscriptionSensorUpdate, cId),
      sensorTypeId(sId),
      sensorReadingLength(srl),
      dataPtr(p) {}

    uint8_t getSensorTypeId() { return sensorTypeId; }
    uint16_t getSensorReadingLength() { return sensorReadingLength; }
    uint8_t* getPtrToData() { return dataPtr; }
};

class Error : public HibikeMessage
{
  private:
    uint8_t errorCode;

  public:
    Error(uint8_t cId, uint8_t ec):
      HibikeMessage(HibikeMessageType.Error, cId),
      errorCode(ec) {}

    uint8_t getErrorCode() { return errorCode; }
};

//// MESSAGE RECEIVING /////////////////////////////////////////////////////////
std::unique_ptr<HibikeMessage> receiveHibikeMessage();
#endif /* HIBIKE_H */
