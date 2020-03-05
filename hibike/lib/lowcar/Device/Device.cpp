#include "Device.h"

const float Device::MAX_SUB_DELAY_MS = 250.0;	//maximum tolerable subscription delay, in ms
const float Device::MIN_SUB_DELAY_MS = 40.0;	//minimum tolderable subscription delay, in ms
const float Device::ALPHA = 0.25;		//tuning parameter for how the interpolation for updating subscription delay should happen

//Device constructor
//initializer list at end of this line initializes the this->msngr and this->led variables properly
Device::Device (DeviceID dev_id, uint8_t dev_year, uint32_t disable_time, uint32_t heartbeat_delay) : msngr(), led()
{
	//initialize primitive variables
	this->sub_delay = 0; //default 0 to signal not subscribed
	this->params = 0; //nothing subscribed to right now
	this->disable_time = disable_time;
	this->heartbeat_delay = heartbeat_delay;
	this->prev_sub_time = this->prev_hb_time = this->prev_hbresp_time = this->curr_time = millis(); //init all these times
	
	this->UID.device_type = dev_id;
	this->UID.year = dev_year;
	this->UID.id = UID_RANDOM; //this is defined at compile time by the flash script
	
	device_enable(); //call device's enable function
}

//universal loop function
//TODO: report errors or do something with them
//TODO: do something when device disables because of time out
void Device::loop ()
{
	Status sts;
	uint16_t *payload_ptr_uint16; //use this to shove 16 bits into the first two elements of the payload (which is of type uint8_t *)
	
	this->curr_time = millis();
	sts = this->msngr->read_message(&(this->curr_msg)); //try to read a new message
	
	if (sts == Status::SUCCESS) { //we have a message!
		switch (this->curr_msg.message_id) {
			case MessageID::PING:
				this->msngr->send_message(MessageID::SUBSCRIPTION_RESPONSE, &(this->curr_msg), params, sub_delay, &UID);
				break;
				
			case MessageID::SUBSCRIPTION_REQUEST:
				this->params = *((uint16_t *) &(this->curr_msg.payload[0])); //update subscribed params
				this->sub_delay = *((uint16_t *) &(this->curr_msg.payload[2]));
				this->msngr->send_message(MessageID::SUBSCRIPTION_RESPONSE, &(this->curr_msg), params, sub_delay, &UID);
				break;
				
			case MessageID::DEVICE_READ:
				//read all specified values from device and store in curr_msg; set payload[0:2] to successfully read params
				payload_ptr_uint16 = (uint16_t *) this->curr_msg.payload; //store the pointer to the front of the payload, cast to uint16_t
				*payload_ptr_uint16 = device_rw_all(&(this->curr_msg), *(uint8_t *)payload_ptr_uint16, RWMode::READ); //payload_ptr_uint16 contains bitmap for rw
				this->msngr->send_message(MessageID::DEVICE_DATA, &(this->curr_msg)); //report device data back to controller
				break;
				
			case MessageID::DEVICE_WRITE:
				//attempt to write specified specified params to device; set payload[0:2] to successfully written params
				payload_ptr_uint16 = (uint16_t *) this->curr_msg.payload; //store pointer to the front of the payload, cast to uint16_t
				*payload_ptr_uint16 = device_rw_all(&(this->curr_msg), *(uint8_t *)payload_ptr_uint16, RWMode::WRITE);  //payload_ptr_uint16 contains bitmap for rw
				device_rw_all(&(this->curr_msg), curr_msg.payload[0], RWMode::READ); //read all values from device and store in curr_msg
				this->msngr->send_message(MessageID::DEVICE_DATA, &(this->curr_msg)); //report device data back to controller
				break;
				
			case MessageID::DEVICE_DISABLE:
				device_disable();
				break;
				
			case MessageID::HEARTBEAT_REQUEST:
				this->msngr->send_message(MessageID::HEARTBEAT_RESPONSE, &(this->curr_msg));
				break;
				
			case MessageID::HEARTBEAT_RESPONSE:
				update_sub_delay(this->curr_msg.payload[1]); //update the subscription delay
				this->prev_hbresp_time = this->curr_time; //this is now the most recent received heartbeat response
				break;
				
			default:
				this->led->toggle();
		}
	} else if (sts == Status::MALFORMED_DATA || sts == Status::PROCESS_ERROR) { //for now just toggle the LED on parsing errors
		this->led->toggle();
	}
	
	//if it's time to send data again
	if ((this->sub_delay > 0) && (this->curr_time - this->prev_sub_time >= this->sub_delay)) {
		this->prev_sub_time = this->curr_time;
		payload_ptr_uint16 = (uint16_t *) this->curr_msg.payload; //store the pointer to the front of the payload, cast to uint16_t
		*payload_ptr_uint16 = device_rw_all(&(this->curr_msg), this->params, RWMode::READ); //read all subscribed values from device and store in curr_msg
		this->msngr->send_message(MessageID::DEVICE_DATA, &(this->curr_msg));
	}
	
	//if it's time to send another heartbeat request
	if ((this->heartbeat_delay > 0) && (this->curr_time - this->prev_hb_time >= this->heartbeat_delay)) {
		this->prev_hb_time = this->curr_time;
		this->msngr->send_message(MessageID::HEARTBEAT_REQUEST, &(this->curr_msg));
	}
	
	//if it's been too long since previous heartbeat response, disable device
	if ((this->disable_time > 0)  && (this->curr_time - this->prev_hbresp_time >= this->disable_time)) {
		device_disable();
	}
	
	device_actions(); //do device-specific actions
}

//************************************************ DEFAULT DEVICE-SPECIFIC METHODS ******************************************* //

//a device uses this function to return data about its state
uint8_t Device::device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len)
{
	return 0; //by default, we read 0 bytes into buffer	
}

//a device uses this function to change a state
uint32_t Device::device_write (uint8_t param, uint8_t *data_buf)
{
	return 0; //by default, we wrote 0 bytes successfully to device
}

//a device uses this function to enable itself
void Device::device_enable ()
{
	return; //by default, enabling the device does nothing
}

//a device uses this function to disable itself
void Device::device_disable ()
{
	return; //by default, disabling the device does nothing
}

//a device uses this function to perform any continuous updates or actions
void Device::device_actions ()
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
				addtl_bytes_written = device_read((uint8_t) param_num, &(msg->payload[bytes_written]), (size_t) sizeof(msg->payload) - bytes_written);
			} else if (mode == RWMode::WRITE){ //write parameter to device; returns # bytes written
				addtl_bytes_written = device_write((uint8_t) param_num, &(msg->payload[bytes_written]));
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

/* Takes in a value sent by a heart beat response packet and computes the new subscription delay. */
void Device::update_sub_delay (uint8_t payload_val)
{
	payload_val = min(payload_val, 100); //don't want the value to be > 100
	float holding = max(Device::MAX_SUB_DELAY_MS * (float) payload_val / 100.0, Device::MIN_SUB_DELAY_MS); //interpolate between min delay and max delay
	this->sub_delay = (uint16_t)(Device::ALPHA * this->sub_delay + (1.0 - Device::ALPHA) * holding); //set the new sub_delay
}
