#ifndef MESSENGER_H
#define MESSENGER_H

#include "defs.h"

class Messenger 
{
public:
	/* constructor; opens Serial connection */
	Messenger ();
	
	/* Handles any type of message and fills in appropriate parameters, then sends onto Serial port
	 * params, delay, and uid only used for subscription responses
	 * Expects *msg to exist
	 * Return a Status enum to report on success/failure
	 */
	Status send_message (MessageID msg_id, message_t *msg, uint16_t params = 0, uint16_t delay = 0, uid_t *uid = NULL);
	
	/* Reads in data from serial port and puts results into msg
	 * Return a Status enum to report on success/failure
	 */
	Status read_message (message_t *msg);
	
private:
	//protocol constants
	const static int MESSAGEID_BYTES;		//bytes in message ID field of packet
	const static int PAYLOAD_SIZE_BYTES; 	//bytes in payload size field of packet
	const static int CHECKSUM_BYTES; 		//bytes in checksum field of packet
	
	const static int UID_DEVICE_BYTES; 		//bytes in device type field of uid
	const static int UID_YEAR_BYTES; 		//bytes in year field of uid
	const static int UID_ID_BYTES; 			//bytes in uid field of uid
	
	
	//helper methods; see source file for more detailed description of functionality
	Status build_msg (MessageID msg_id, message_t *msg, uint16_t params = 0, uint16_t delay = 0, uid_t *uid = NULL);
	int append_payload (message_t *msg, uint8_t *data, uint8_t length);
	void message_to_byte (uint8_t *data, message_t *msg);
	uint8_t checksum (uint8_t *data, int length);
	size_t cobs_encode (uint8_t *dst, const uint8_t *src, size_t src_len);
	size_t cobs_decode(uint8_t *dst, const uint8_t *src, size_t src_len);
};

#endif
