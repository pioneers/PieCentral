#ifndef LINE_FOLLOWER_H
#define LINE_FOLLOWER_H

#include "../../base/Device.h"
#include "../../base/defs.h"

#define NUM_PINS 3 //number of pins used on device

class LineFollower : public Device
{
public:
	//constructs a LineFollower; simply calls generic Device constructor with device type and year
	LineFollower ();
	
	//overridden functions from Device class; see descriptions in Device.h
	virtual uint8_t device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len);
	virtual void device_enable ();
	
private:
	uint8_t pins[NUM_PINS] = {A0, A1, A2}; //pins that the line follower reads data from (defined in defs.h)
};

#endif