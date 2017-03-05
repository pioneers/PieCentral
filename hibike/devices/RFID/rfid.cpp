#include "rfid.h"
#include <SPI.h>
#include <MFRC522.h> 

#define RST_PIN 9
#define SS_PIN 10

// Instantiate RFID Object
MFRC522 mfrc522(SS_PIN, RST_PIN);
// each device is responsible for keeping track of it's own params
uint8_t value0;

// normal arduino setup function, you must call hibike_setup() here
void setup() {
  hibike_setup();
  // Setup sensor input
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
  if ( ! mfrc522.PICC_IsNewCardPresent()) {
    return;
  }
  value0 = mfrc522.uid.uidByte[0];

  hibike_loop();
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
  if (len < sizeof(value0) && param == 0) {
      return 0;
  }
  ((uint8_t*)data)[0] = value0;
  return sizeof(value0);
  return 0;
}
