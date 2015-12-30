#include "hibike_device.h"

message_t hibikeBuff;

uint64_t prevTime, currTime, heartbeat;
uint8_t param;
uint32_t value;
uint16_t subDelay;
uint8_t data_update_buf[MAX_PAYLOAD_SIZE];
bool led_enabled;

void hibike_setup() {
  Serial.begin(115200);
  prevTime = millis();
  subDelay = 0;

  // Setup Error LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  led_enabled = false;

}

void hibike_loop() {
  currTime = millis();

  // Check for Hibike packets
  if (Serial.available() > 1) {
    if (read_message(&hibikeBuff) == -1) {
      toggleLED();
    } else {
      //send_data_update(&hibikeBuff.messageID, sizeof(hibikeBuff.messageID));
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
          send_device_response(param, device_update(param, value));
          break;

        case DEVICE_STATUS:
          param = hibikeBuff.payload[0];
          send_device_response(param, device_status(param));
          break;

        case DEVICE_RESPONSE:
          // Unsupported packet
          toggleLED();
          break;
        case PING_:
          send_subscription_response(&UID, subDelay);
          break;
        case 8:
          {
          //send_data_update(&hibikeBuff.messageID, sizeof(hibikeBuff.messageID));
          send_description_response(DESCRIPTION);
          //send_data_update((uint8_t *)&x, sizeof(x));
          break;
          }

        default:
          //send_data_update(&hibikeBuff.messageID, sizeof(hibikeBuff.messageID));

          // Uh oh...
          toggleLED();
      }
    }
  }
  if (currTime - heartbeat >= 1000) {
    heartbeat = currTime;
    toggleLED();
  }
  if ((subDelay > 0) && (currTime - prevTime >= subDelay)) {
    prevTime = currTime;
    send_data_update(data_update_buf, data_update(data_update_buf, MAX_PAYLOAD_SIZE));
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
