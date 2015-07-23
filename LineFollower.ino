#include "hibike_message.h"

int inPin = 1;
int ledPin = 13;
int data;
unsigned long ms;
unsigned long ms_compare;
uint32_t time_passed;
hibike_message_t* m;
int subscribed;

uint16_t len = 0xFFFF;

  
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(inPin, INPUT);
  pinMode(ledPin, OUTPUT);
  ms = millis();
}

void loop() {
  // put your main code here, to run repeatedly:
  data = analogRead(inPin);
  ms_compare = millis();
  m = recieve_message();
  // message parsing
  if (m) {
    switch (m->message_id) {
    case SUBSCRIPTION_REQUEST:
      send_subscription_response(0x00);
      subscribed = 1;
      break;
    case SUBSCRIPTION_SENSOR_UPDATE:
      if (subscribed) {
        ms = millis();
        time_passed = (uint32_t) (ms - ms_compare);
        if (time_passed > update_delay_time) {
          // find what the inputs to the following function are
          send_subscription_update(0x00, len, uint8_t *data_ptr);
        }
      }
      break;
    //error case
    case 0xFF:
      send_error(OxFF);
      break;
    default: break;
    }
  }
}
