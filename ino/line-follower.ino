#include "hibike_message.h"

#define IN_PIN = 1;

uint32_t data;
uint64_t time_last_message_sent;

bool subscribed;
uint32_t subscription_delay;

hibike_message_t* m;

void setup() {
  hibike_init(2); // ID arbitrarily chosen for now
  pinMode(IN_PIN, INPUT);
}

void loop() {
  data = analogRead(IN_PIN);
  uint64_t curr_time = millis();
  if (subscribed && curr_time - time_last_message_sent > subscription_delay) {
    send_subscription_update(SENSOR_TYPE.LINE_FOLLOWER, sizeof(data), &data);
    time_last_message_sent = curr_time;
  }
  m = recieve_message();
  if (m) {
    switch (m->message_id) {
      case HIBIKE_MESSAGE.SUBSCRIPTION_REQUEST:
        // TODO: actually validate the result and send back
        //       descriptive errors if something failed
        send_subscription_response(SUBSCRIPTION_RESPONSE.SUCCESS);
        if (m->payload.delay) {
          subscribed = true;
          subscription_delay = m->payload.delay;
        } else {
          subscribed = false;
        }
        break;
      case HIBIKE_MESSAGE.ERROR:
        Serial.println("ERROR");
        // TODO: implement better error handling
        break;
      // TODO: implement other message types
    }
  }
}
