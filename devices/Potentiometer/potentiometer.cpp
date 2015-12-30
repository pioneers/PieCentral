#include "potentiometer.h"
#include <Servo.h>
//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  POTENTIOMETER,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////
char *DESCRIPTION = 
"{"
"    \"deviceID\": \"0x02\","
"    \"deviceName\": \"Potentiometer\","
"    \"dataFormat\": {"
"        \"formatString\": \"<HHHH\","
"        \"parameters\": ["
"            {"
"                \"scalingFactor\": 1023.0,"
"                \"machineName\": \"value0\","
"                \"humanName\": \"Potentiometer 0\""
"            },"
"            {"
"                \"scalingFactor\": 1023.0,"
"                \"machineName\": \"value1\","
"                \"humanName\": \"Potentiometer 1\""
"            },"
"            {"
"                \"scalingFactor\": 1023.0,"
"                \"machineName\": \"value2\","
"                \"humanName\": \"Potentiometer 2\""
"            },"
"            {"
"                \"scalingFactor\": 1023.0,"
"                \"machineName\": \"value3\","
"                \"humanName\": \"Potentiometer 3\""
"            }"
"        ]"
"    },"
"    \"params\": ["
"        \"dataUpdate\""
"    ]"
"}";

message_t hibikeBuff;

//int params[NUM_PARAMS];

uint64_t prevTime, currTime, heartbeat;
uint32_t value;
uint16_t subDelay;
uint16_t data[NUM_PINS];
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
    pinMode(pins[i], INPUT_PULLUP);
  }

  subDelay = 0;
  heartbeat = 0;
}


void loop() {
  // Read sensor
  for (int i = 0; i < NUM_PINS; i++) {
      data[i] = analogRead(pins[i]);  
  }
  currTime = millis();

  // Check for Hibike packets
  if (Serial.available() > 1) {
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
          // Unsupported packet
          toggleLED();
          break;

        case DEVICE_STATUS:
          // Unsupported packet
          toggleLED();
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

  //Send data update
  currTime = millis();
  if ((subDelay > 0) && (currTime - prevTime >= subDelay)) {
    prevTime = currTime;
    send_data_update((uint8_t *)data, sizeof(data));
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
