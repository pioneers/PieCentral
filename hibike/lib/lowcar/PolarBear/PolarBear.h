#ifndef POLARBEAR_H
#define POLARBEAR_H

#include "Device.h"
#include "PID.h"
#include "LED.h"
#include "defs.h"

#define feedback A3
#define PWM1 6
#define PWM2 9

class PolarBear : public Device
{
public:
	PolarBear ();
	virtual uint8_t device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len);
	virtual uint32_t device_write (uint8_t param, uint8_t *data_buf);
	virtual void device_enable ();
	virtual void device_disable ();
	virtual void device_actions ();

private:
	float pwmInput;
	uint8_t driveMode;
	bool motorEnabled;
	float deadBand;
	int currpwm1;
	int currpwm2;
	int delayMod;
	float dpwm_dt;
	PID *pid;
	int sign(float x);
	void drive(float target);
};

#endif
