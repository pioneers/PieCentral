#include "example_device.h"

message_t hibikeRecieveBuff = {};
message_t hibikeSendBuff = {};
uint64_t prevTime, currTime;
uint16_t subDelay;
uint8_t data;
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

    // Check for Hibike packets
    if (read_message(&hibikeRecieveBuff) != -1) {
        switch (hibikeRecieveBuff.messageID) {
            case SUBSCRIPTION_REQUEST:
                // change subDelay and send SUB_RESP
                subDelay = payload_to_uint16(hibikeRecieveBuff.payload);

                // this should really be managed by a sub-function
                memset(&hibikeRecieveBuff, 0, sizeof(message_t));
                hibikeRecieveBuff.messageID = SUBSCRIPTION_RESPONSE;
                uint16_to_payload(subDelay, hibikeRecieveBuff.payload);
                hibikeRecieveBuff.payload_length = 2;
                send_message(&hibikeRecieveBuff);
                break;

            case SUBSCRIPTION_RESPONSE:
                // Unsupported packet
                toggleLED();
                break;

            case DATA_UPDATE:
                // Unsupported packet
                toggleLED();
                break;

            default:
                // Uh oh...
                toggleLED();
        }
    }

    // Send data update
    currTime = millis();
    if (currTime - prevTime >= subDelay) {
        prevTime = currTime;

        // This should really be managed by a sub-function
        memset(&hibikeSendBuff, 0, sizeof(message_t));
        hibikeSendBuff.messageID = SUBSCRIPTION_RESPONSE;
        *hibikeSendBuff.payload = data;
        hibikeSendBuff.payload_length = 1;
        send_message(&hibikeSendBuff);
    }
}

// Assumes payload is little endian
uint16_t payload_to_uint16(uint8_t* payload) {
    return ((uint16_t) payload[0]) + (((uint16_t) payload[1]) << 8);
}

// Assumes payload is little endian
void uint16_to_payload(uint16_t data, uint8_t* payload) {
    payload[0] = (uint8_t) (data & 0xFF);
    payload[1] = (uint8_t) (data >> 8);
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