#ifndef MESSENGER_H
#define MESSENGER_H

#include "cobs.h"
#include "defs.h"

class Messenger 
{
public:
	Messenger (); //constructor, fill in parameters if necessary
	
	//general send and read message functions
	int send_message (message_t* msg);
	int read_message (message_t* msg);
}

#endif
