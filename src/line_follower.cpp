#include "../lib/hibike_message.h"

#define IN_PIN 1
#define CONTROLLER_ID 0 // arbitrarily chosen for now

uint32_t data;
uint64_t timeLastMessageSent;

uint32_t subscriptionDelay;

std::unique_ptr<HibikeMessage> m;

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
    SubscriptionSensorUpdate(CONTROLLER_ID, SensorType.LineFollower,
                             sizeof(data), (uint8_t*) &data).send();
    timeLastMessageSent = currTime;
  }
  m.reset(receiveHibikeMessage());
  // need to check up on whether a unique_ptr containing null evaluates to false
  if (m) {
    switch (m->getMessageId()) {
      case HibikeMessageType.SubscriptionRequest:
        uint32_t sd = m->getSubscriptionDelay();
        subscriptionDelay = sd;
        SubscriptionResponse(CONTROLLER_ID).send();
        break;
      case HibikeMessageType.Error:
        // TODO: implement error handling and retries
        break;
      default:
        // TODO: implement other message types
        break;
    }
  }
}
