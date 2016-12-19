#include "rfid.h"

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

// each device is responsible for keeping track of it's own params
uint32_t params[NUM_PARAMS];

// normal arduino setup function, you must call hibike_setup() here
void setup() {
  hibike_setup();
    // Setup sensor input
  SPI.begin();
  mfrc522.PCD_Init();
  mfrc522.PCD_DumpVersionToSerial();
}

// normal arduino loop function, you must call hibike_loop() here
// hibike_loop will look for any packets in the serial buffer and handle them
void loop() {
  //look for new cards
  if( ! mfrc522.PICC_IsNewCardPresent()){
  	return;
  }
  //select one of the cards
  if(!mfrc522.PICC_ReadCardSerial()){
  	return;
  }

  params[0] = &((uint32_t*)mfrc522.uid.uidByte);

  hibike_loop();
}

uint32_t device_write(uint8_t param, uint8_t* value, size_t len) {
	return 0;
}



// you must implement this function. It is called when the device receives a DeviceUpdate packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_update(uint8_t param, uint32_t value) {
  return ~((uint32_t) 0);
}

// you must implement this function. It is called when the devie receives a DeviceStatus packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_status(uint8_t param) {
  if (param < NUM_PARAMS) {
    return params[param];
  }
  return ~((uint32_t) 0);
}




// you must implement this function. It is called with a buffer and a maximum buffer size.
// The buffer should be filled with appropriate data for a DataUpdate packer, and the number of bytes
// added to the buffer should be returned. 
//
// You can use the helper function append_buf.
// append_buf copies the specified amount data into the dst buffer and increments the offset

uint8_t device_data_update(int param, uint8_t* data_update_buf, size_t buf_len) {
  if(MAX_PAYLOAD_SIZE - buf_len < sizeof(uint32_t)|| param!=0){
    return 0;
  }
  data_update_buf[0] = &((uint8_t)params[0]);//casting fun
  return sizeof(uint32_t);
}
