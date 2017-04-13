#include "rfid.h"
#include <SPI.h>
#include <MFRC522.h> 

#define RST_PIN 9
#define SS_PIN 10

// Instantiate RFID Object
MFRC522 mfrc522(SS_PIN, RST_PIN);
// each device is responsible for keeping track of it's own params
uint8_t id;
uint8_t tag_detect;
bool del = false;

// normal arduino setup function, you must call hibike_setup() here
void setup() {
  hibike_setup(); //use default heartbeat rates. look at /lib/hibike/hibike_device.cpp for exact values
  SPI.begin();
  mfrc522.PCD_Init();
}


// normal arduino loop function, you must call hibike_loop() here
// hibike_loop will look for any packets in the serial buffer and handle them
// hibike_loop will call device_write and device_read

void loop() {
  // do whatever you want here
  // note that hibike will only process one packet per call to hibike_loop()
  // so exessive delays here will affect hibike.
  // Look for new cards
  hibike_loop();
  // Checks if there is a card at reader
  if ( ! mfrc522.PICC_IsNewCardPresent()) {
    // The sensor is too slow, so we have to delay the read by one loop
    // The del makes sure that the id and tag_detect doesn't update for
    // one cycle of the loop after finding a tag
    if (del) {
      tag_detect = 0;
      id = 0;
    }
    del = true;
    return;
  }
  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) {
    id = 0;
    tag_detect = 0;
    return;
  }
  // Grab first byte of ID
  id = mfrc522.uid.uidByte[0];
  tag_detect = 1;
  del = false;
}


// You must implement this function.
// It is called when the device receives a Device Write packet from the BBB.
// Updates param to new value passed in data.
//    param   -   Parameter index
//    data    -   buffer to get the value from, in little-endian bytes
//    len     -   size of the buffer for overflow checking
//
//   return   -   number of bytes read from data on success; otherwise return 0

uint32_t device_write(uint8_t param, uint8_t* data, size_t len) {
  return 0;
}


// You must implement this function.
// It is called when the device wants to send data to the BBB.
// Modifies data to contain the parameter value.
//    param   -   Parameter index
//    data    -   buffer to return data in, little-endian
//    len     -   size of the buffer for overflow checking
//
//    return  -   number of bytes writted to data on success; 0 otherwise

uint8_t device_read(uint8_t param, uint8_t* data, size_t len) {
  switch (param) {
    case ID:
      if (len < sizeof(id)) {
        return 0;
      }
      ((uint8_t*)data)[0] = id;
      return sizeof(id);
      break;
    case TAG_DETECT:
      if (len < sizeof(tag_detect)) {
        return 0;
      }
      ((uint8_t*)data)[0] = tag_detect;
      return sizeof(tag_detect);
      break;
    default:
      return 0;
  }
  return 0;
}

// You must implement this function.
// It is called when the BBB sends a message to the Smart Device tellinng the Smart Device to disable itself.
// Consult README.md, section 6, to see what exact functionality is expected out of disable.
void device_disable() {
//Do nothing.  This is a sensor.
}
