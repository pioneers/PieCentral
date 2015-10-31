#include "example_device.h"
#include <Servo.h>
message_t hibikeBuff;
hibike_uid_t UID = {
  1,        // Device Type
  0,        // Year
  0xBEEFBEEF,    // ID
};
Servo servo;
int params[NUM_PARAMS];

uint64_t prevTime, currTime, heartbeat;
uint32_t value;
uint16_t subDelay;
uint8_t data, reading_offset, param;
bool led_enabled;

void setup() {
  Serial.begin(115200);
  prevTime = millis();
  subDelay = 0;
  memset(&params, 0, sizeof(params[0])*NUM_PARAMS);

  // Setup Error LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  led_enabled = false;

  // Setup sensor input
  pinMode(IN_PIN, INPUT_PULLUP);
  subDelay = 0;
  heartbeat = 0;

  servo.attach(6);
}

void loop() {
  // Read sensor
  data = digitalRead(IN_PIN);
  currTime = millis();

  // Check for Hibike packets
  if (Serial.available()) {
    if (read_message(&hibikeBuff) == -1) {
      toggleLED();
    } else {
      switch (hibikeBuff.messageID) {
        case SUBSCRIPTION_REQUEST:
          // change subDelay and send SUB_RESP
          subDelay = payload_to_uint16(hibikeBuff.payload);
          send_subscription_response(&UID, subDelay);
          break;

        case SUBSCRIPTION_RESPONSE:
          // Unsupported packet
          toggleLED();
          break;

        case DATA_UPDATE:
          // Unsupported packet
          toggleLED();
          break;

        case DEVICE_UPDATE:
          param = hibikeBuff.payload[0];
          value = *((uint32_t*) &hibikeBuff.payload[DEVICE_PARAM_BYTES]);
          update_param(param, value);
          send_device_response(param, params[param]);

          // REMOVE!!!
          if (param == 6) {
            servo.write(value);
          }
          break;

        case DEVICE_STATUS:
          // Unsupported packet
          param = hibikeBuff.payload[0];
          send_device_response(param, params[param]);
          toggleLED();
          break;

        case DEVICE_RESPONSE:
          // Unsupported packet
          toggleLED();
          break;

        default:
          // Uh oh...
          toggleLED();
      }
    }
  }

  if (currTime - heartbeat >= 1000) {
    heartbeat = currTime;
    toggleLED();
  }

  //Send data update
  currTime = millis();
  if ((subDelay > 0) && (currTime - prevTime >= subDelay)) {
    prevTime = currTime;
    uint8_t _data[1] = {data};
    send_data_update(_data, 1);
  }
}


void update_param(uint8_t param, uint32_t value) {
  params[param] = value;
}




void toggleLED() {
  if (led_enabled) {
    digitalWrite(LED_PIN, LOW);
    led_enabled = false;
  } else {
    digitalWrite(LED_PIN, HIGH);
    led_enabled = true;
  }
}