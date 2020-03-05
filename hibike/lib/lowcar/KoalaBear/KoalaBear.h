#ifndef KOALABEAR_H
#define KOALABEAR_H

#include "Device.h"
#include "PID.h"
#include "LEDKoala.h"
#include "pindefs_koala.h"
#include "defs.h"
#include <SPI.h>

class KoalaBear : public Device
{
public:
	KoalaBear ();
	virtual uint8_t device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len);
	virtual uint32_t device_write (uint8_t param, uint8_t *data_buf);
	virtual void device_enable ();
	virtual void device_disable ();
	virtual void device_actions ();

private:
	float* desired_speeds;
	uint8_t* drivemodes;
	bool* enabled;
	float* deadbands;
	LEDKoala* led;
	int prev_led_time;
	int curr_led_mtr;
	
	int sign (float x);
	void drive (float target, uint8_t mtr);
	void write_current_lim ();
	void read_current_lim ();
	void electrical_setup();
};

#endif
