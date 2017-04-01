#include "hibike_device.h"

message_t hibike_buff;
uint16_t params, old_params, sub_delay;

//Heartbeat settings.  
uint32_t disable_latency, heartbeat_delay;
const uint32_t default_disable_latency = 1000; //default number of ms without heartbeat untill disable.
const uint32_t default_heartbeat_delay = 200; //default time between sending heartbeat requests.

//a bunch of values that are used to store times, for the various hearbeat states.
uint64_t prev_sub_time, curr_time, sent_heartbeat, resp_heartbeat, prevHeartTimer;

//various options to show LED on pin 13, if one exists, as a hibike indicator.  Don't use with APMs.
led_state heartbeat_state;
bool led_enabled;

void hibike_setup(uint32_t _disable_latency, uint32_t _heartbeat_delay) {
  //heartbeat_delay to 0 to not send heartbeat Requests
  //disable_latency to 0 to not disable on lack of heartbeats.
  Serial.begin(115200);
  prev_sub_time = millis();
  sub_delay = 0;  //0 is a default that means that nothing is subscribed to it. 
  disable_latency = _disable_latency;  //this long without recieving a heartbeat response to disable myself.
  heartbeat_delay = _heartbeat_delay; //Send a quest for heartbeat this fast.

  // Setup Error LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  heartbeat_state = RESTING;
  led_enabled = false;
}

void hibike_setup() //call hibike_setup with default values.  Useful since most devices will probably do it this way
{
	hibike_setup(default_disable_latency,default_heartbeat_delay);
}

void hibike_loop() {
  curr_time = millis();
  // Check for Hibike packets
  if (Serial.available() > 1) {
    if (read_message(&hibike_buff) == -1) {
      toggleLED();
    } else {
      int offset;
      switch (hibike_buff.messageID) {

        case SUBSCRIPTION_REQUEST:
          // change sub_delay and send SUB_RESP
          sub_delay = *((uint16_t*) &hibike_buff.payload[2]);
          params = *((uint16_t*) &hibike_buff.payload[0]);
          send_subscription_response(params, sub_delay, &UID);
          break;

        case SUBSCRIPTION_RESPONSE:
          // Unsupported packet
          toggleLED();
          break;

        case DEVICE_WRITE:
          //loop over params
          old_params = params;
          offset = 2;
          params = *((uint16_t*)&hibike_buff.payload[0]);
          for (uint16_t count = 0; (params >> count) > 0; count++) {
            if (params & (1<<count)){
              int status = device_write(count, &hibike_buff.payload[offset], hibike_buff.payload_length-offset);
              if(status){
                offset += status;}
              else{
                params = params & ~(1<<count);}
              }
          }

          //write values
          *((uint16_t*)&hibike_buff.payload[0]) = params;
          send_data_update(*((uint16_t*) &hibike_buff.payload[0]));
          params = old_params;
          break;

        case DEVICE_READ:

          send_data_update(*((uint16_t*) &hibike_buff.payload[0]));
          break;

        case DEVICE_DATA:
          // Unsupported packet
          toggleLED();
          break;

        case DEVICE_DISABLE:
          device_disable();
          break;

        case HEART_BEAT_REQUEST:
          // send heart beat response
          send_heartbeat_response(1);
          break;

        case HEART_BEAT_RESPONSE:
          resp_heartbeat = curr_time;
          break;

        case PING:
          send_subscription_response(params, sub_delay, &UID);
          break;

        default:
          // Uh oh...
          toggleLED();
      }
    }
  }

  if ((sub_delay > 0) && (curr_time - prev_sub_time >= sub_delay)) {
    prev_sub_time = curr_time;
    send_data_update(params);
  }

  if ( ( (heartbeat_delay) > 0) && ( (curr_time - prevHeartTimer) >= heartbeat_delay) )
  {
    //send heartbeat request
    send_heartbeat_request(1); //1 is just a placeholder for future use.
    prevHeartTimer = curr_time;
  }

  if ( (disable_latency > 0)  && ( (curr_time - resp_heartbeat) >= disable_latency)   ) 
  {
    device_disable(); //on sensor specific device
  }
}

void toggleLED() {
  if (led_enabled) {
    digitalWrite(LED_PIN, LOW);
    led_enabled = false;
  } else {
    digitalWrite(LED_PIN, HIGH);
    led_enabled = true;
  }
}
