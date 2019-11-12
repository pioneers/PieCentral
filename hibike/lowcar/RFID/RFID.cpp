#include "../RFID.h"

#define RST_PIN 9
#define SS_PIN 10

//default constructor simply specifies DeviceID and year to generic constructor and initializes variables
RFID::RFID () : Device (DeviceID::RFID, 1)
{
	this->tag_detector = new MFRC522(SS_PIN, RST_PIN); //instatiate the RFID object
	this->id = 0;
	this->tag_detect = 0;
	this->delay = false;
}

uint8_t RFID::device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len)
{	
	switch ((RFID_Param) param) { //switch the incoming parameter (cast to RFID_Param)
		case RFID_Param::ID:
			if (data_buf_len < sizeof(this->id)) {
				return 0;
			}
			//put the 32-bit long ID parameter into the first 32 bits of the data_buf
			((uint32_t *)data_buf)[0] = this->id;
			return sizeof(this->id);
			
		case RFID_Param::TAG_DETECT:
			if (data_buf_len < sizeof(this->tag_detect)) {
				return 0;
			}
			//put the 8-bit long tag_detect parameter into the first 8 bits of the data_buf
			data_buf[0] = this->tag_detect;
			return sizeof(tag_detect);
			
		default:
			return 0;
	}
}

void device_enable ()
{
	SPI.begin(); //begin SPI (what's this?)
	this->tag_detector->PCD_Init(); //initialize the RFID object
}

void device_actions ()
{
	/* If we either don't sense a card or can't read the UID, we invalidate the data
	 * The sensor is too slow, so we have to delay the read by one loop
	 * The delay makes sure that id and tag_detect don't update for
	 * one cycle of the loop after finding a tag
	 */
	if (!this->tag_detector->PICC_IsNewCardPresent() || !this->tag_detector->PICC_ReadCardSerial()) {
		if (this->delay) {
			this->id = 0; //clear the id to invalidate it
			this->tag_detect = 0; //no tag detected
		}
		this->del = true;
		return; //after resetting all our values, we return
	}
	
	//Otherwise, if there is a card that we can read the UID from, we grab the data
	//and set tag_detect to 1 to signal that we have a new tag UID
	this->id =	(uint32_t)(this->tag_detector.uid.uidByte[2]) << 16 |
				(uint32_t)(this->tag_detector.uid.uidByte[1]) << 8  |
				(uint32_t)(this->tag_detector.uid.uidByte[0]);
	this->tag_detect = 1;
	this->del = false; //reset the delay
}
