#ifndef DEVICE_H
#define DEVICE_H

#include "defs.h"
#include "Messenger.h"
#include "StatusLED.h"

class Device
{	
public: 
	//******************************************* UNIVERSAL DEVICE METHODS ************************************** //
	/* Constructor with default args (times in ms)
	 * set disable_time to 0 if no disable on lack of heartbeat requests
	 * set heartbeat_delay to 0 if no sending heartbeat requests
	 * calls device_enable to enable the device
	 * dev_id and dev_year are the device type and device year of the device
	 */
	Device (DeviceID dev_id, uint8_t dev_year, uint32_t disable_time = 1000, uint32_t heartbeat_delay = 200);
	
	/* Generic device loop function that wraps all device actions
	 * asks Messenger to read a new packet, if any, and responds appropriately
	 * sends heartbeat requests and device data at set intervals
	 */
	void loop ();
	
	//******************************************* DEVICE-SPECIFIC METHODS ************************************** //
	/* These functions are meant to be overridden by overridden by each device as it sees fit. 
	 * There are default dummy implementations of all these functions that do nothing so that the program will not
	 * crash if they are not overwritten (for example, you don't need to overwrite device_write for a device that
	 * has only read-only parameters). 
	 */
	
	/* This function is called when the device receives a Device Read packet. 
	 * It modifies DATA_BUF to contain the most recent value of parameter PARAM.
	 * param			-   Parameter index (0, 1, 2, 3 ...)
	 * data_buf 		-   Buffer to return data in, little-endian
	 * buf_len			-   Number of bytes available in data_buf to store data
	 * 
	 * return			-   sizeof(<parameter_value>) on success; 0 otherwise
	 */
	virtual uint8_t device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len);
	
	/* This function is called when the device receives a Device Write packet.
	 * Updates PARAM to new value contained in DATA.
	 * param			-   Parameter index (0, 1, 2, 3 ...)
	 * data_buf	 		-   Contains value to write, little-endian
	 *
	 * return			-   sizeof(<bytes_written>) on success; 0 otherwise
	 */
	virtual uint32_t device_write (uint8_t param, uint8_t *data_buf);
	
	/* This function is called in the Device constructor 
	 * (or potentially on receiving a Device Enable packet in the future).
	 * It should do whatever setup is necessary for the device to operate.
	 */
	virtual void device_enable ();
	
	/* This function is called when receiving a Device Disable packet, or 
	 * when the controller has stopped responding to heartbeat requests.
	 * It should do whatever cleanup is necessary for the device to disable.
	 */
	virtual void device_disable ();
	
	/* This function is called each time the device goes through the main loop.
	 * Any continuously updating actions the device needs to do should be placed
	 * in this function.
	 * IMPORTANT: This function should not block!
	 */
	virtual void device_actions ();

private:
	//******************************* PRIVATE VARIABLES AND HELPER METHOD ************************************** //
	const static float MAX_SUB_DELAY_MS;	//maximum tolerable subscription delay, in ms
	const static float MIN_SUB_DELAY_MS;	//minimum tolerable subscription delay, in ms
	const static float ALPHA;				//subscription delay interpolation tuning constant
	
	Messenger *msngr; //deals with all encoding/decoding and sending/reading of messages on serial
	StatusLED *led;
	uid_t UID; //UID of this device
	uint16_t params; //bitmap for which parameters are subscribed to on this device
	uint16_t sub_delay; //time between successive subscription responses (ms)
	uint32_t disable_time, heartbeat_delay; //time betweeen heartbeat requests (ms)
	uint64_t prev_sub_time, prev_hb_time, prev_hbresp_time, curr_time; //variables to hold times (ms)
	message_t curr_msg; //current message being processed
	
	//read or write data to device (more detail in source file)
	uint16_t device_rw_all (message_t *msg, uint16_t params, RWMode mode);
	//update subscription delays on heartbeat response packets
	void update_sub_delay (uint8_t payload_val);
};

#endif
