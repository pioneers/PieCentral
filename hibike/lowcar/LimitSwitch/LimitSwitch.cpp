#include "../LimitSwitch.h"

//Defines pins used only by the Limit Switch
#define IN_0 A0
#define IN_1 A1
#define IN_2 A2

//default constructor simply specifies DeviceID and year to generic constructor
LimitSwitch::LimitSwitch () : Device (DeviceID::LIMIT_SWITCH, 0)
{
	;
}

uint8_t LimitSwitch::device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len)
{
	//if not enough space to read something, or undefined parameter
	if (data_buf_len < sizeof(uint8_t) || param >= NUM_SWITCHES) {
    	return 0;
  	}

	//put pin value into data_buf and return the state of the switch
  	data_buf[0] = digitalRead(this->pins[param]) == HIGH;
	return sizeof(bool);
}

void LimitSwitch::device_enable ()
{
	//set all pins to INPUT mode
	for (int i = 0; i < NUM_SWITCHES; i++) {
		pinMode(pins[i], INPUT);
	}
}