#include "../LineFollower.h"

const static int LineFollower::NUM_PINS = 3; //number of pins used for I/O for LineFollower
//pins that the line follower reads data from (defined in defs.h)
const static uint8_t LineFollower::pins[LineFollower::NUM_PINS] = {Analog::IO0, Analog::IO1, Analog::IO1};

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
	*data_ptr_float = ((float) analogRead(LineFollower::pins[param])) / 1023;
	
	return sizeof(float);
}

void LineFollower::device_enable ()
{
	//set all pins to INPUT mode
	for (int i = 0; i < LineFollower::NUM_PINS; i++) {
		pinMode(LineFollower::pins[i], INPUT);
	}
}