#include "servo_control.h"
#include <Servo.h>
//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  SERVO_CONTROL,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////
char *DESCRIPTION = 
"{"
"    \"deviceID\": \"0x07\","
"    \"deviceName\": \"ServoControl\","
"    \"dataFormat\": {"
"        \"formatString\": \"\","
"        \"parameters\": []"
"    },"
"    \"params\": ["
"        \"dataUpdate\","
"        \"servo0\","
"        \"servo1\","
"        \"servo2\","
"        \"servo3\""
"    ]"
"}";

message_t hibikeBuff;

//int params[NUM_PARAMS];
Servo servos[NUM_PINS];


uint64_t prevTime, currTime, heartbeat;
uint8_t param, servo;
uint32_t value;
uint16_t subDelay;
uint8_t pins[NUM_PINS] = {IN_0, IN_1, IN_2, IN_3};
bool led_enabled;

void setup() {
  Serial.begin(115200);
  prevTime = millis();
  subDelay = 0;


  // Setup Error LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  led_enabled = false;

  // Setup sensor input
  for (int i = 0; i < NUM_PINS; i++) {
    servos[i].attach(pins[i]);
  }

  subDelay = 0;
  heartbeat = 0;
}


void loop() {
  // Read sensor
  currTime = millis();

  // Check for Hibike packets
  if (Serial.available() > 1) {
    if (read_message(&hibikeBuff) == -1) {
      toggleLED();
    } else {
      switch (hibikeBuff.messageID) {
        case SUBSCRIPTION_REQUEST:
          // Unsupported packet
          toggleLED();
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
          servo = param - 1;
          value = *((uint32_t*) &hibikeBuff.payload[DEVICE_PARAM_BYTES]);
          if (servo < NUM_PINS) {
            servos[servo].write(value);
            send_device_response(param, servos[servo].read());
          } else {
            toggleLED();
          }
          break;

        case DEVICE_STATUS:
          param = hibikeBuff.payload[0];
          servo = param -1;
          if (servo < NUM_PINS) {
            send_device_response(param, servos[servo].read());
          } else {
            toggleLED();
          }
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

  if (currTime - heartbeat >= 1000) {
    heartbeat = currTime;
    toggleLED();
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
