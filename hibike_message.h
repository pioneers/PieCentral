#ifndef HIBIKE_H
#define HIBIKE_H
#include "Arduino.h"

enum class HibikeMessageType {
  SubscriptionRequest,
  SubscriptionResponse,
  SensorUpdate,
  Error = 0xFF,
};

enum class SensorType {
  LimitSwitch,
  LineFollower,
};

enum class ErrorCode {
  InvalidMessageType = 0xFB,
  MalformedMessage   = 0xFC,
  InvalidArduinoId   = 0xFD,
  ChecksumMismatch   = 0xFE,
  GenericError       = 0xFF,
};

//// CLASS DEFINITIONS //////////////////////////////////////////////////////
class HibikeMessage
{
  protected:
    HibikeMessageType messageId;
    uint8_t controllerId;
    uint8_t checksum;
    bool checksumCalculated;
    virtual void calculateChecksum() = 0;

  public:
    HibikeMessage(HibikeMessageType mId, uint8_t cId):
      messageId(mId),
      controllerId(cId),
      checksum(0),
      checksumCalculated(false) {}

    // getter functions. We want to ensure that HibikeMessages cannot be further altered
    // after construction, and thus we choose to have the class fields protected and their
    // values accessible using getters. Note that depending
    HibikeMessageType getMessageId() { return messageId; }
    uint8_t getControllerId() { return controllerId; }
    uint8_t getChecksum() { calculateChecksum(); return checksum; }
    virtual void send() = 0;
};

class SubscriptionRequest : public HibikeMessage
{
  private:
    uint32_t subscriptionDelay;
    void calculateChecksum();

  public:
    SubscriptionRequest(uint8_t cId, uint32_t sd):
      HibikeMessage(HibikeMessageType::SubscriptionRequest, cId),
      subscriptionDelay(sd) {}

    uint32_t getSubscriptionDelay() { return subscriptionDelay; }
    void send();
};

class SubscriptionResponse : public HibikeMessage
{
  private:
    void calculateChecksum();

  public:
    SubscriptionResponse(uint8_t cId):
      HibikeMessage(HibikeMessageType::SubscriptionResponse, cId) {}

    void send();
};

class SensorUpdate : public HibikeMessage
{
  private:
    SensorType sensorTypeId;
    uint16_t sensorReadingLength;
    uint8_t *dataPtr;
    void calculateChecksum();

  public:
    SensorUpdate(uint8_t cId, SensorType sId, uint16_t srl, uint8_t *p):
      HibikeMessage(HibikeMessageType::SensorUpdate, cId),
      sensorTypeId(sId),
      sensorReadingLength(srl),
      dataPtr(p) {}

    SensorType getSensorTypeId() { return sensorTypeId; }
    uint16_t getSensorReadingLength() { return sensorReadingLength; }
    uint8_t* getPtrToData() { return dataPtr; }
    void send();
};

class Error : public HibikeMessage
{
  private:
    ErrorCode errorCode;
    void calculateChecksum();

  public:
    Error(uint8_t cId, ErrorCode ec):
      HibikeMessage(HibikeMessageType::Error, cId),
      errorCode(ec) {}

    ErrorCode getErrorCode() { return errorCode; }
    void send();
};

//// MESSAGE RECEIVING /////////////////////////////////////////////////////////
HibikeMessage* receiveHibikeMessage();
#endif /* HIBIKE_H */
