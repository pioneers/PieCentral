#include "ServoControl.h"

const int ServoControl::NUM_SERVOS = 2;
const int ServoControl::SERVO_0 = 5;
const int ServoControl::SERVO_1 = 6;
const int ServoControl::SERVO_CENTER = 1500; //center position on servo, in microseconds (?)
const int ServoControl::SERVO_RANGE = 1000; //range of movement of servo is SERVO_CENTER +/- SERVO_RANGE
const uint8_t ServoControl::pins[] = {SERVO_0, SERVO_1};

Servo *servo0 = new Servo();
Servo *servo1 = new Servo();
Servo servos[2] = { *servo0, *servo1 };

//runs default Device constructor and then disables all servos at start
//initializes this->servos[] to contain references to the two Servo objects in initializer list
ServoControl::ServoControl() : Device(DeviceID::SERVO_CONTROL, 1) //, servo0(), servo1() //, servos{ *servo0, *servo1 }
{
	this->positions = new float[NUM_SERVOS];
	for (int i = 0; i < ServoControl::NUM_SERVOS; i++) {
		this->positions[i] = 0.0;
	}
	disable_all();
}

//Device functions

//Reads value in positions associated with servo at param to buffer
//Returns size of float if successful and 0 otherwise
uint8_t ServoControl::device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len)
{
	if (data_buf_len < sizeof(float)) {
		return 0;
	}
	float *float_buf = (float *) data_buf;
	float_buf[0] = this->positions[param];
	return sizeof(float);
}

//Attaches servo at param to corresponding pin if not attached yet
//Updates value in positions array to value
//Updates pulse width associated with specified servo
//Returns size of bytes written if successful and 0 otherwise
uint32_t ServoControl::device_write (uint8_t param, uint8_t *data_buf)
{
	float value = ((float *) data_buf)[0];
	if (value < -1 || value > 1) {
		return 0;
	}
	
	//if servo isn't attached yet, attach the pin to the servo object
	if (!servos[param].attached()) {
		servos[param].attach(this->pins[param]);
	}
	this->positions[param] = value;
	servos[param].writeMicroseconds(ServoControl::SERVO_CENTER + (this->positions[param] * ServoControl::SERVO_RANGE / 2.0));
	return sizeof(float);
}

//Disables all the servos on call
void ServoControl::device_disable()
{
	disable_all();
}

//Helper Functions

//disables all servos by detaching them
void ServoControl::disable_all() {
	for (int i = 0; i < ServoControl::NUM_SERVOS; i++) {
		servos[i].detach();
	}
}
