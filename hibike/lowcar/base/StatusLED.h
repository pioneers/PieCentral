#ifndef STATUSLED_H
#define STATUSLED_H

#include "defs.h"

class StatusLED
{
public:
	//sets up the status LED and configures the pin
	StatusLED ();
	
	//toggles LED between on and off
	void toggle ();
	
private:
	bool led_enabled; //keeps track of whether LED is on or off
};

#endif
