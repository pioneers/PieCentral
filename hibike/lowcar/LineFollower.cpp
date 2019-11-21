#include "LineFollower.h"

const int LineFollower::NUM_PINS = 3; //number of pins used for I/O for LineFollower
//pins that the line follower reads data from (defined in defs.h)
const uint8_t LineFollower::pins[] = {(const uint8_t) Analog::IO0, (const uint8_t) Analog::IO1, (const uint8_t) Analog::IO2};

//default constructor simply specifies DeviceID and year to generic constructor
LineFollower::LineFollower () : Device (DeviceID::LINE_FOLLOWER, 1)
{
	;
}

uint8_t LineFollower::device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len)
{
	//if not enough space to read something, or undefined parameter
	if (data_buf_len < sizeof(uint8_t) || param > 2) {
		return 0;
	}
	
	//use data_ptr_float to shove 10-bit sensor reading into the data_buf (even though data_buf is of type uint8_t)
	float *data_ptr_float = (float *)data_buf;
	*data_ptr_float = ((float) analogRead(this->pins[param])) / 1023;
	
	return sizeof(float);
}

void LineFollower::device_enable ()
{
	//set all pins to INPUT mode
	for (int i = 0; i < LineFollower::NUM_PINS; i++) {
		pinMode(LineFollower::pins[i], INPUT);
	}
}
