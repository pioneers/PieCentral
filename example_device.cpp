#include "example_device.h"

message_t hibikeRecieveBuff = {};
message_t hibikeSendBuff = {};
const hibike_uid_t UID = {0, 0, 123456789};
uint64_t prevTime, currTime, heartbeat;
uint16_t subDelay;
uint8_t data, reading_offset;
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
    pinMode(IN_PIN, INPUT);

}

void loop() {
    // Read sensor
    data = digitalRead(IN_PIN);
    currTime = millis();

    // Check for Hibike packets
    if (Serial.available()) {
        if (read_message(&hibikeRecieveBuff) == -1) {
            toggleLED();
        }

        switch (hibikeRecieveBuff.messageID) {
            case SUBSCRIPTION_REQUEST:
                // change subDelay and send SUB_RESP
                reading_offset = 0;
                subDelay = uint16_from_message(&hibikeRecieveBuff, &reading_offset);
                memset(&hibikeRecieveBuff, 0, sizeof(message_t));
                subscription_response(&hibikeSendBuff, UID, subDelay);
                send_message(&hibikeSendBuff);
                break;

            case SUBSCRIPTION_RESPONSE:
                // Unsupported packet
                while (Serial.available() > 0) {
                    Serial.read();
                }
                toggleLED();
                break;

            case DATA_UPDATE:
                // Unsupported packet
                while (Serial.available() > 0) {
                    Serial.read();
                }
                toggleLED();
                break;

            default:
                // Uh oh...
                while (Serial.available() > 0) {
                    Serial.read();
                }
                toggleLED();
        }
    }

    if (currTime - heartbeat >= 1000) {
        heartbeat = currTime;
        toggleLED();
    }

    //Send data update
    currTime = millis();
    if (subDelay != 0 && currTime - prevTime >= subDelay) {
        prevTime = currTime;
        data_update(&hibikeSendBuff, &data, 1);
        send_message(&hibikeSendBuff);
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