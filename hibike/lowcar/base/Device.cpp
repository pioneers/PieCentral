#include "Device.h"

//Device constructor, fill in parameters
Device::Device (uint32_t disable_time = 1000, uint32_t heartbeat_delay = 200)
{
	//initialize variables
	msngr = new Messenger();
	led = new StatusLED();
	
	this->disable_time = disable_time;
	this->heartbeat_delay = heartbeat_delay;
	this->sub_delay = 0; //default 0 to signal not subscribed
}

//setup function
void Device::setup ()
{
	//call this device's setup function
}

//loop function
void Device::loop ()
{
	//do any continuous work if needed
	//try to get data from Messenger
	//do something with the device if needed
	//manage heartbeats
}

//functions that need to be overridden by specific devices
virtual uint32_t Device::device_write (uint8_t param, uint8_t *data, size_t len);
virtual uint8_t Device::device_read (uint8_t param, uint8_t *data, size_t len);
virtual void Device::device_disable ();
virtual uint8_t Device::device_enable ();	
