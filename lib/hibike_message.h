#ifndef HIBIKE_H
#define HIBIKE_H
#include "Arduino.h"
#include "assert.h"

/*
 * qq. Arduino doesn't support C++11 currently, and thus we can't used scoped
 * enums here. Note that the transition to scoped enums should be made as soon
 * as it becomes possible
 */
// Message types
#define SUBSCRIPTION_REQUEST        0x00
#define SUBSCRIPTION_RESPONSE       0x01
#define SUBSCRIPTION_SENSOR_UPDATE  0x02
#define SENSOR_UPDATE_REQUEST       0x03
#define SENSOR_UPDATE               0x04
#define ERROR                       0xFF
// Sensor types
#define LIMIT_SWITCH                0x00
#define LINE_FOLLOWER               0x01
// Error codes
#define SUCCESS                     0x00
#define INVALID_MESSAGE_TYPE        0xFB
#define MALFORMED_MESSAGE           0xFC
#define INVALID_ARDUINO_ID          0xFD
#define CHECKSUM_MISMATCH           0xFE


// top level abstract HibikeMessage class
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
      messageId(mId), controllerId(cId), checksum(0), checksumCalculated(false) {}
    // getter functions. We want to ensure that HibikeMessages cannot be further altered
    // after construction, and thus we choose to have the class fields private and their
    // values accessible using getters. Note that depending
    uint8_t getMessageId() { return messageId; }
    uint8_t getControllerId() { return controllerId; }
    uint8_t getChecksum();
    virtual void send() = 0;
};

class SubscriptionRequest : public HibikeMessage
{
  private:
    uint32_t subscriptionDelay;

  public:
    SubscriptionRequest(uint8_t cId, uint32_t sd):
      HibikeMessage(SUBSCRIPTION_REQUEST, cId), subscriptionDelay(sd) {}

    uint32_t getSubscriptionDelay() { return subscriptionDelay; }
}

class SubscriptionResponse : public HibikeMessage
{
  private:
    uint8_t errorCode;

  public:
    SubscriptionResponse(uint8_t cId, uint8_t ec):
      HibikeMessage(SUBSCRIPTION_RESPONSE, cId), errorCode(ec) {}

    uint8_t getErrorCode() { return errorCode; }
}

class SubscriptionSensorUpdate : public HibikeMessage
{
  private:
    uint8_t sensorTypeId;
    uint16_t sensorReadingLength;
    uint8_t *dataPtr;

  public:
    SubscriptionSensorUpdate(uint8_t cId, uint8_t sId, uint16_t srl, uint8_t *p):
      HibikeMessage(SUBSCRIPTION_SENSOR_UPDATE, cId),
      sensorTypeId(sId), sensorReadingLength(srl), dataPtr(p) {}

    uint8_t getSensorTypeId() { return sensorTypeId; }
    uint16_t getSensorReadingLength() { return sensorReadingLength; }
    uint8_t* getPtrToData() { return dataPtr; }
}

class Error : public HibikeMessage
{
  private:
    uint8_t errorCode;

  public:
    Error(uint8_t cId, uint8_t ec):
      HibikeMessage(SUBSCRIPTION_RESPONSE, cId), errorCode(ec) {}
    uint8_t getErrorCode() { return errorCode; }
}

///////////////////////////// Message receiving /////////////////////////////
HibikeMessage* receiveHibikeMessage();
#endif /* HIBIKE_H */
