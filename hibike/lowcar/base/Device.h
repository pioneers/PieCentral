#ifndef DEVICE_H
#define DEVICE_H

#include "defs.h"
#include "Messenger.h"

class Device
{
private:
	Messenger *msngr;
	
public:
	Device (); //constructor, fill in parameters
	
	//Device setup and loop functions
	void setup ();
	void loop ();
	
	//Device-specific read, write, enable, disable functions
	virtual uint32_t device_write (uint8_t param, uint8_t *data, size_t len);
	virtual uint8_t device_read (uint8_t param, uint8_t *data, size_t len);
	virtual void device_disable ();
	virtual uint8_t device_enable (); 
};

#endif