#include "hibike_device.h"

message_t hibikeBuff;
uint16_t params, old_params, subDelay;
uint32_t value, disable_latency;
uint64_t prevTime, currTime, sent_heartbeat, resp_heartbeat;
led_state heartbeat_state;
bool led_enabled;

void hibike_setup(uint32_t _disable_latency) {
  Serial.begin(115200);
  prevTime = millis();
  subDelay = 0;
  disable_latency = _disable_latency;

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

        case DEVICE_DISABLE:
          device_disable();
          break;

        case HEART_BEAT_REQUEST:
          // send heart beat response
          send_heartbeat_response(1);
          break;

        case HEART_BEAT_RESPONSE:
          resp_heartbeat = currTime;
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

  if ((subDelay > 0) && (currTime - prevTime >= subDelay)) {
    prevTime = currTime;
    send_data_update(params);
  }

  if ((currTime - resp_heartbeat) > disable_latency) {
    device_disable(); //on sensor specific device
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
