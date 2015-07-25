#include "hibike_message.h"

#define IN_PIN = 3;
#define LED_PIN = 13;
int data;
unsigned long long ms;
unsigned long long ms_compare;
uint64_t time_passed;
hibike_message_t* m;
int subscribed;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(IN_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  ms = millis();
}

void loop() {
  // put your main code here, to run repeatedly:
  data = digitalRead(IN_PIN);
  ms_compare = millis();
  m = recieve_message();
  // message parsing
  if (subscribed) {
    ms = millis();
    time_passed = ms - ms_compare;
      if (time_passed > update_delay_time) {
        // find what the inputs to the following function are
        send_subscription_update(SENSOR_TYPE.LIMIT_SWITCH, sizeof(data), &data);
      }
    }
  if (m) {
    switch (m->message_id) {
    case HIBIKE_MESSAGE.SUBSCRIPTION_REQUEST:
      HIBIKE_MESSAGE.SUBSCRIPTION_RESPONSE = SUCCESS;
      send_subscription_response(0x00);
      subscribed = 1;
      break;
    case HIBIKE_MESSAGE.SUBSCRIPTION_SENSOR_UPDATE:
      break;
    //error case
    case HIBIKE_MESSAGE.ERROR:
      Serial.print(HIBIKE_MESSAGE.ERROR)
      send_error(HIBIKE_MESSAGE.ERROR);
      break;
    default: break;
    }
  }
}
