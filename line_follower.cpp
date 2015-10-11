#include "hibike_message.h"

#define IN_PIN 1
#define CONTROLLER_ID 0 // arbitrarily chosen for now

uint32_t data;

// Interval between updates, in milliseconds
uint32_t subscriptionInterval = 0;
// Time at which to send the next subscription 
uint32_t subscriptionTime = 0;

HibikeMessage* m;

void setup() {
  Serial.begin(115200);
  pinMode(IN_PIN, INPUT);
}

void loop() {
  data = digitalRead(IN_PIN);

  uint64_t currTime = millis();
  // uncomment the line below for fun data spoofing
  data = (uint32_t) (currTime) & 0xFFFFFFFF;

  if (subscriptionInterval && (currTime > subscriptionDelay)) {
    SensorUpdate(CONTROLLER_ID, SensorType::LineFollower, sizeof(data), (uint8_t*) &data).send();
  }

  m = receiveHibikeMessage();
  if (m) {
    switch (m->getMessageId()) {
      case HibikeMessageType::SubscriptionRequest:
        {
          subscriptionInterval = ((SubscriptionRequest*) m)->getSubscriptionDelay();
          subscriptionTime = currTime + subscriptionInterval;
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
