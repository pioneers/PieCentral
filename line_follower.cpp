#include "hibike_message.h"

#define IN_PIN 1
#define CONTROLLER_ID 0 // arbitrarily chosen for now

uint32_t data;
uint64_t timeLastMessageSent;

uint32_t subscriptionDelay;

HibikeMessage* m;

void setup() {
  Serial.begin(115200);
  pinMode(IN_PIN, INPUT);
}

void loop() {
  data = digitalRead(IN_PIN);

  // uncomment the line below for fun data spoofing
  // data = (uint8_t) millis() & 0xFF;

  uint64_t currTime = millis();
  if (subscriptionDelay && currTime - timeLastMessageSent > subscriptionDelay) {
    SensorUpdate(CONTROLLER_ID, SensorType::LineFollower,
                 sizeof(data), (uint8_t*) &data).send();
    timeLastMessageSent = currTime;
  }
  m = receiveHibikeMessage();
  if (m) {
    switch (m->getMessageId()) {
      case HibikeMessageType::SubscriptionRequest:
        {
          uint32_t sd = ((SubscriptionRequest*) m)->getSubscriptionDelay();
          subscriptionDelay = sd;
          SubscriptionResponse(CONTROLLER_ID).send();
          break;
        }
      case HibikeMessageType::SubscriptionResponse:
      case HibikeMessageType::SensorUpdate:
      case HibikeMessageType::Error:
      default:
        // TODO: implement error handling and retries
        // TODO: implement other message types
        break;
    }
    delete m;
  }
}
