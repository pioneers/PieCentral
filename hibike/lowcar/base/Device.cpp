#include "Device.h"

//Device constructor
Device::Device (uint32_t disable_time = 1000, uint32_t heartbeat_delay = 200)
{
	//initialize variables
	this->msngr = new Messenger();
	this->led = new StatusLED();

	this->sub_delay = 0; //default 0 to signal not subscribed
	this->params = 0; //nothing subscribed to right now
	this->disable_time = disable_time;
	this->heartbeat_delay = heartbeat_delay;
	this->prev_sub_time = this->prev_hb_time = this->prev_hbresp_time = this->curr_time = millis(); //init all these times
	
	device_enable(); //call device's enable function
}


//TODO: report errors or do something with them
//TODO: do something when device disables because of time out
void Device::loop ()
{
	Status sts;
	
	this->curr_time = millis();
	sts = msngr->read_message(&(this->curr_msg)); //try to read a new message
	
	if (sts == Status::SUCCESS) { //we have a message!
		switch (curr_msg.message_id) {
			case MessageID::PING:
				msngr->send_message(MessageID::SUBSCRIPTION_RESPONSE, &(this->curr_msg), params, sub_delay, &UID);
				break;
				
			case MessageID::SUBSCRIPTION_REQUEST:
				this->params = *((uint16_t *) &(this->curr_msg.payload[0])); //update subscribed params
				this->sub_delay = *((uint16_t *) &(this->curr_msg.payload[2]));
				msngr->send_message(MessageID::SUBSCRIPTION_RESPONSE, &(this->curr_msg), params, sub_delay, &UID);
				break;
				
			case MessageID::DEVICE_READ:
				device_rw_all(&(this->curr_msg), success_params, RWMode::READ); //read all values from device and store in curr_msg
				msngr->send_message(MessageID::DEVICE_DATA, &(this->curr_msg)); //report device data back to controller
				break;
				
			case MessageID::DEVICE_WRITE:
				//attempt to write specified specified params to device; set payload[0:1] to successfully written params
				*((uint16_t *) &(this->curr_msg.payload[0])) = device_rw_all(&(this->curr_msg), curr_msg->payload[0], RWMode::WRITE);
				device_rw_all(&(this->curr_msg), success_params, RWMode::READ); //read all values from device and store in curr_msg
				msngr->send_message(MessageID::DEVICE_DATA, &(this->curr_msg)); //report device data back to controller
				break;
				
			case MessageID::DEVICE_DISABLE:
				device_disable();
				break;
				
			case MessageID::HEARTBEAT_REQUEST:
				msngr->send_message(MessageID::HEARTBEAT_RESPONSE, &(this->curr_msg));
				break;
				
			case MessageID::HEARTBEAT_RESPONSE:	
				this->sub_delay = *((uint16_t *) &(this->curr_msg.payload[1])); //update the subscription delay
				this->prev_hbresp_time = this->curr_time; //this is now the most recent received heartbeat response
				break;
				
			default:
				led->toggle();
		}
	} else if (sts == Status::MALFORMED_DATA || sts == Status::PROCESS_ERROR) { //for now just toggle the LED on parsing errors
		led->toggle();
	}
	
	//if it's time to send data again
	if ((this->sub_delay > 0) && (this->curr_time - this->prev_sub_time >= this->sub_delay)) {
		this->prev_sub_time = this->curr_time;
		device_rw_all(&(this->curr_msg), success_params, RWMode::READ); //read all values from device and store in curr_msg
		msngr->send_message(MessageID::DEVICE_DATA, &(this->curr_msg));
	}
	
	//if it's time to send another heartbeat
	if ((this->heartbeat_delay > 0) && (this->curr_time - this->prev_hb_time >= this->heartbeat_delay)) {
		this->prev_hb_time = this->curr_time;
		msngr->send_message(MeessageID::HEARTBEAT_REQUEST, &(this->curr_msg));
	}
	
	//if it's been too long since previous heartbeat, disable device
	if ((this->disable_time > 0)  && (this->curr_time - this->prev_hbresp_time >= this->disable_time)) {
		device_disable();
	}
	
	device_actions(); //do device-specific actions
}

//************************************************ DEFAULT DEVICE-SPECIFIC METHODS ******************************************* //

//a device uses this function to return data about its state
virtual uint8_t Device::device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len)
{
	return 0; //by default, we read 0 bytes into buffer	
}

//a device uses this function to change a state
virtual uint32_t Device::device_write (uint8_t param, uint8_t *data_buf)
{
	return 0; //by default, we wrote 0 bytes successfully to device
}

//a device uses this function to enable itself
virtual void Device::device_enable ()
{
	return; //by default, enabling the device does nothing
}

//a device uses this function to disable itself
virtual void Device::device_disable ()
{
	return; //by default, disabling the device does nothing
}

//a device uses this function to perform any continuous updates or actions
virtual void Device::device_actions ()
{
	return; //by default, device does nothing on every loop
}

//************************************************************* HELPER METHOD *************************************************** //

/* Takes in a message_t to work with, a param bitmap, and whether to write to or read from the device.
 * on RWMode::READ -- attempts to read specified params into msg->payload, in order
 * on RWMode::WRITE -- attemps to write all specified params from msg->payload to device
 * In both cases, msg->payload_length set to number of bytes successfully written (to msg->payload or to the device).
 * Returns bitmap corresponding to all params that were successfully read from or written to.
 */
uint16_t Device::device_rw_all (message_t *msg, uint16_t params, RWMode mode) 
{
	int bytes_written = 2; //number of bytes we've written so far into the payload of the current message OR number of bytes successfully written to device
	int addtl_bytes_written; //number of bytes written by a call to device_read or device_write (addtl = additional)
	
	//loop over params and attempt to read or write data for requested bits
	for (uint16_t param_num = 0; (params >> param_num) > 0; param_num++) {
		if (params & (1 << param_num)) {
			if (mode == RWMode::READ) { //read parameter into payload at next available bytes in payload; returns # bytes read (= # bytes written to payload)
				addtl_bytes_written = device_read((uint8_t) param_num, msg->payload[bytes_written], (size_t) sizeof(msg->payload) - bytes_written);
			} else if (mode == RWMode::WRITE){ //write parameter to device; returns # bytes written
				addtl_bytes_written = device_write((uint8_t) param_num, msg->payload[bytes_written]);
			}
			
			if (addtl_bytes_written != 0) { //if we wrote something, update bytes_written
				bytes_written += addtl_bytes_written;
			} else { //turn that bit off so that caller can see that we failed to read or write this param
				params &= ~(1 << param_num);
			}
		}
	}
	msg->payload_length = bytes_written; //put how many bytes we wrote to as payload length
	
	return params;
}
