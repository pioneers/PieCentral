#ifndef LIMIT_SWITCH_H
#define LIMIT_SWITCH_H

#include "Device.h"
#include "defs.h"

#define NUM_SWITCHES 3 //number of pins used on device

class LimitSwitch : public Device
{
public:
	//constructs a LimitSwitch; simply calls generic Device constructor with device type and year
	LimitSwitch ();
	
	//overridden functions from Device class; see descriptions in Device.h
	virtual uint8_t device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len);
	virtual void device_enable ();
	
private:
	uint8_t pins[NUM_SWITCHES] = {IN_0, IN_1, IN_2}; //pins that the limit switch reads data from (defined in defs.h)
};

#endif