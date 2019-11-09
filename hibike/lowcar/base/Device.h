#ifndef DEVICE_H
#define DEVICE_H

#include "defs.h"
#include "Messenger.h"
#include "StatusLED.h"

class Device
{	
public:
	//constructor with default args (times in ms)
	Device (uint32_t disable_time = 1000, uint32_t heartbeat_delay = 200); 
	
	//Device setup and loop functions
	void setup ();
	void loop ();
	
	//Device-specific read, write, enable, disable functions
	virtual uint32_t device_write (uint8_t param, uint8_t *data, size_t len);
	virtual uint8_t device_read (uint8_t param, uint8_t *data, size_t len);
	virtual void device_disable ();
	virtual uint8_t device_enable (); 

private:
	Messenger *msngr;
	StatusLED *led;
	uint16_t sub_delay; //time between successive subscription responses (ms)
	uint32_t disable_time, heartbeat_delay; //time betweeen heartbeat requests (ms)
	uint64_t prev_sub_time, prev_hb_time, curr_time; //variables to hold times (ms)
};

#endif