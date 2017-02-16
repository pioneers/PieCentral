#include "hibike_device.h"

message_t hibikeBuff;
uint64_t prevTime, currTime, heartbeatTime;
uint16_t params, old_params;
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
      int offset;
      switch (hibikeBuff.messageID) {

        case SUBSCRIPTION_REQUEST:
          // change subDelay and send SUB_RESP
          subDelay = *((uint16_t*) &hibikeBuff.payload[2]);
          params = *((uint16_t*) &hibikeBuff.payload[0]);
          send_subscription_response(params, subDelay, &UID);
          break;

        case SUBSCRIPTION_RESPONSE:
          // Unsupported packet
          toggleLED();
          break;

        case DEVICE_WRITE:
          //loop over params
          old_params = params;
          offset = 2;
          params = *((uint16_t*)&hibikeBuff.payload[0]);
          for (uint16_t count = 0; (params >> count) > 0; count++) {
            if (params & (1<<count)){
              int status = device_write(count, &hibikeBuff.payload[offset], hibikeBuff.payload_length-offset);
              if(status){
                offset += status;}
              else{
                params = params & ~(1<<count);}
              }
          }

          //write values
          *((uint16_t*)&hibikeBuff.payload[0]) = params;
          send_data_update(*((uint16_t*) &hibikeBuff.payload[0]));
          params = old_params;
          break;

        case DEVICE_READ:

          send_data_update(*((uint16_t*) &hibikeBuff.payload[0]));
          break;

        case DEVICE_DATA:
          // Unsupported packet
          toggleLED();
          break;

        case PING:
          send_subscription_response(params, subDelay, &UID);
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

  if ((subDelay > 0) && (currTime - prevTime >= subDelay)) {
    prevTime = currTime;
    send_data_update(params);
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
