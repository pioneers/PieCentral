#include "Device.h"

//Device constructor, fill in parameters
Device::Device ()
{
	msngr = new Messenger();
	//something something
}

//setup function
void Device::setup ()
{
	//initialize variables
	//instantiate Messenger
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
