#include "hibike_device.h"

char *DESCRIPTION = DESCRIPTOR;

message_t hibikeBuff;

uint64_t prevTime, currTime, heartbeatTime;
uint8_t param;
uint32_t value;
uint16_t subDelay;
led_state heartbeat_state;
bool led_enabled;

void hibike_setup() {
  Serial.begin(115200);
  prevTime = millis();
  subDelay = 0;

  // Setup Error LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  heartbeat_state = RESTING;
  led_enabled = false;

}

void hibike_loop() {
  currTime = millis();
  // Check for Hibike packets
  if (Serial.available() > 1) {
    if (read_message(&hibikeBuff) == -1) {
      toggleLED();
    } else {
      switch (hibikeBuff.messageID) {

        case SUBSCRIPTION_REQUEST:
          // change subDelay and send SUB_RESP
          subDelay = *((uint16_t*) &hibikeBuff.payload[0]);
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
          param = hibikeBuff.payload[0] - 1;
          value = *((uint32_t*) &hibikeBuff.payload[DEVICE_PARAM_BYTES]);
          send_device_response(param + 1, device_update(param, value));
          break;

        case DEVICE_STATUS:
          param = hibikeBuff.payload[0] - 1;
          send_device_response(param + 1, device_status(param));
          break;

        case DEVICE_RESPONSE:
          // Unsupported packet
          toggleLED();
          break;

        case PING_:
          send_subscription_response(&UID, subDelay);
          break;

        case DESCRIPTION_REQUEST:
          send_description_response(DESCRIPTION);
          break;

        default:
          // Uh oh...
          toggleLED();
      }
    }
  }

  // Hearbeat
  switch (heartbeat_state) {
    case RESTING:
      if (currTime - heartbeatTime >= 1700) {
        heartbeatTime = currTime;
        digitalWrite(LED_PIN, HIGH);
        led_enabled = true;
        heartbeat_state = FIRST_BEAT;
      }
      break;

    case FIRST_BEAT:
      if (currTime - heartbeatTime >= 100) {
        heartbeatTime = currTime;
        digitalWrite(LED_PIN, LOW);
        led_enabled = false;
        heartbeat_state = BREAK;
      }
      break;

    case BREAK:
      if (currTime - heartbeatTime >= 100) {
        heartbeatTime = currTime;
        digitalWrite(LED_PIN, HIGH);
        led_enabled = true;
        heartbeat_state = SECOND_BEAT;
      }
      break;

    case SECOND_BEAT:
      if (currTime - heartbeatTime >= 100) {
        heartbeatTime = currTime;
        digitalWrite(LED_PIN, LOW);
        led_enabled = false;
        heartbeat_state = RESTING;
      }
      break;
  }

  // DataUpdates
  if ((subDelay > 0) && (currTime - prevTime >= subDelay)) {
    prevTime = currTime;
    hibikeBuff.messageID = DATA_UPDATE;
    hibikeBuff.payload_length = data_update(hibikeBuff.payload, sizeof(hibikeBuff.payload));
    if (hibikeBuff.payload_length > MAX_PAYLOAD_SIZE) {
      toggleLED();
    } else {
      send_message(&hibikeBuff);
    }
  }

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
