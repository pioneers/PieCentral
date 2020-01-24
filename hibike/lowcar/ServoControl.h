#ifndef SERVO_CONTROL_H
#define SERVO_CONTROL_H

#include "Device.h"
#include "defs.h"
#include <Servo.h>

class ServoControl : public Device
{
public:	
	//Constructor
	ServoControl();
	
	//Overridden functions
	//Comments/descriptions can be found in source file and in Device.h
	virtual uint8_t device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len);
	virtual uint32_t device_write (uint8_t param, uint8_t *data_buf);
	virtual void device_disable (); //calls helper disableAll() to detach all servos

private:
	//class constants and variables
	const static int NUM_SERVOS, SERVO_0, SERVO_1, SERVO_CENTER, SERVO_RANGE;
	const static uint8_t pins[];
	
	float *positions;
	
	//detaches all servos
	void disable_all ();
};

#endif
