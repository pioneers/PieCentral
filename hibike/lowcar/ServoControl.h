#ifndef SERVO_CONTROL_H
#define SERVO_CONTROL_H

#include "Device.h"
#include "defs.h"
#include <Servo.h>

#define NUM_PINS 2

#define SERVO_0 5
#define SERVO_1 6

#define SERVO_RANGE 1000
#define SERVO_CENTER 1500

class ServoControl : public Device
{
public:
    ServoControl();
    // Overridden functions
    // Comments/descriptions can be found in source file
    virtual uint8_t device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len);
    virtual uint32_t device_write (uint8_t param, uint8_t *data_buf);
    virtual void device_disable (); //calls helper disableAll() to detach all servos

private:
	//class constants and variables
	const static int NUM_SERVOS, SERVO_0, SERVO_1, SERVO_CENTER, SERVO_RANGE;
    const static uint8_t pins[ServoControl::NUM_PINS];
	
	Servo servo0, servo1;
	Servo servos[LimitSwitch::NUM_SERVOS];
    float positions[LimitSwitch::NUM_SERVOS];
	
    //detaches all servos
    void disableAll ();
};

#endif
