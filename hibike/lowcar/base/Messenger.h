#ifndef MESSENGER_H
#define MESSENGER_H

#include "defs.h"
#include <cstring.h>

class Messenger 
{
public:
	/* constructor; opens Serial connection */
	Messenger ();
	
	/* Handles any type of message and fills in appropriate parameters, then sends onto Serial port
	 * params, delay, and uid only used for subscription responses
	 * Expects *msg to exist
	 * Return -1 if not all data bytes were written to serial, as reported by Serial.write()
	 */
	int send_message (MessageID msg_id, message_t *msg, uint16_t params = 0, uint16_t delay = 0, uid_t *uid = NULL);
	
	/* Reads in data from serial port and puts results into msg
	 * return -1 on errors
	 */
	int read_message (message_t *msg);
	
private:
	//helper methods; see source file for more detailed description of functionality
	int format_msg (MessageID msg_id, message_t *msg, uint16_t params = 0, uint16_t delay = 0, uid_t *uid = NULL);
	int append_payload(message_t *msg, uint8_t *data, uint8_t length);
	void message_to_byte(uint8_t *data, message_t *msg);
	uint8_t checksum (uint8_t *data, int length);
	size_t cobs_encode (uint8_t *dst, const uint8_t *src, size_t src_len);
	size_t cobs_decode(uint8_t *dst, const uint8_t *src, size_t src_len) 
}

#endif
