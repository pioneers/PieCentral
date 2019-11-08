#include "Messenger.h"

//protocol constants
#define MAX_PAYLOAD_SIZE    100
#define MESSAGEID_BYTES     1
#define PAYLOAD_SIZE_BYTES  1
#define CHECKSUM_BYTES      1

#define MAX_FRAGMENT_SIZE   (MAX_PAYLOAD_SIZE - 1)

#define UID_DEVICE_BYTES    2
#define UID_YEAR_BYTES      1
#define UID_ID_BYTES        8
#define UID_BYTES           (UID_DEVICE_BYTES+UID_YEAR_BYTES+UID_ID_BYTES)

#define DEVICE_PARAM_BYTES   1
#define DEVICE_VALUE_BYTES   4
#define DEVICE_BYTES         (DEVICE_PARAM_BYTES+DEVICE_VALUE_BYTES)

Messenger::Messenger ()
{
	Serial.begin(115200); //open Serial (USB) connection
}

int Messenger::send_message (message_t *msg)
{
	//handles any type of message and fills in appropriate parameters, then sends onto Serial port
	
	return 0;
}

int Messenger::read_message (message_t *msg)
{
	return 0;
}

