#include "YogiBear.h"
#include "ui.h"
#include "pid.h"
#include "encoder.h"
#include "current_limit.h"
#include "motor.h"

//A space for constants.
float pwmInput = 0; //Value that is received from hibike and is the goal PWM
uint8_t driveMode = 0; //0 for manual, 1 for PID Velocity, 2 for PID Position

double pos = 0; //these both used to be volatile, but PID library doesn't convert well between volatiles and not-volatiles in c++
double vel = 0;

bool hibike = false;
bool continualPrint = false;
unsigned long heartbeat = 0;
unsigned long hibikeHeartbeatLimit = 500;





//Timers.
#include <FlexiTimer2.h>


void setup()
{
  motorSetup();
  currentLimitSetup();
  encoderSetup();
  PIDSetup();

  if(hibike)
  {
    hibike_setup();
  }
  else
  {
    Serial.begin(115200);
  }


}

/* 
   Manual Controls:
   s <x> - sets pwm to x
   c     - clears faults
   p <x> - turns on PID mode, velocity if x = v, position if x = p
   m     - turns on manual input mode
   e     - enables motor
   d     - disables motor
   r     - displays 1 print of all readable values
   t     - toggles continual printing of pos and vel
   b     - send heartbeat
   h     - switch hibike mode
   z     - switch human controls
   w <x> <y> - writes the value y to the variable x
*/
void loop()
{
  if(hibike)
  {
    hibike_loop();
  }
  else
  {
    manual_ui();
  }

}




// You must implement this function.
// It is called when the device receives a Device Write packet.
// Updates param to new value passed in data.
//    param   -   Parameter index
//    data    -   value to write, in little-endian bytes
//    len     -   number of bytes in data
//
//   return  -   size of bytes written on success; otherwise return 0

uint32_t device_write(uint8_t param, uint8_t* data, size_t len) {
  switch (param) 
  {
  	case ENABLE:
  	  if (len == 1) {
  	  	if (data[0] == 0) {
  	  		disable();
  	  	} else {
  	  		enable();
  	  	}
  	  }
  	  break;
    case COMMAND_STATE: 
      if (len == 1) {
      	driveMode = data[0];
      	if (driveMode == 0) {
      		disablePID();
      	} else if (driveMode == 1) {
      		enableVel();
      	} else {
      		enablePos();
      	}
      	return 1;
      }
      break;
    case DUTY_CYCLE: 
      if (len == 4) {
      	pwmInput = data[0];
      	return 1;
      }
      break;
    case PID_POS_SETPOINT: 
      if (len == 4) {
      	setPosSetpoint(data[0]);
      	return 1;
      }
      break;
    case PID_POS_KP: 
      if (len == 4) {
      	setPosKP(data[0]);
      	return 1;
      }
      break;
    case PID_POS_KI: 
      if (len == 4) {
      	setPosKI(data[0]);
      	return 1;
      }
      break;
    case PID_POS_KD: 
      if (len == 4) {
      	setPosKD(data[0]);
      	return 1;
      }
      break;
    case PID_VEL_SETPOINT: 
      if (len == 4) {
      	setVelSetpoint(data[0]);
      	return 1;
      }
      break;
    case PID_VEL_KP: 
      if (len == 4) {
      	setVelKP(data[0]);
      	return 1;
      }
      break;
    case PID_VEL_KI: 
      if (len == 4) {
      	setVelKI(data[0]);
      	return 1;
      }
      break;
    case PID_VEL_KD: 
      if (len == 4) {
      	setVelKD(data[0]);
      	return 1;
      }
      break;
    case CURRENT_THRESH: 
      if (len == 4) {
      	setCurrentThreshold(data[0]);
      	return 1;
      }
      break;
    case ENC_POS: 
      if (len == 4) {
      	if((uint32_t) data[0] == 0) {
      		zeroEncoder();
      	}
      }
      break;
    case ENC_VEL: 
      break;
    case MOTOR_CURRENT: 
      break;
    default:
      return 0;
    }

  /*
    case VALUE_0:
      value0 = (uint8_t) read_num_bytes(data, sizeof(value0));
      return sizeof(value0);
      break;
    case VALUE_1:
      value1 = (uint8_t) read_num_bytes(data, sizeof(value1));
      return sizeof(value1);
      break;
    case VALUE_2:
      value2 = (uint16_t) read_num_bytes(data, sizeof(value2));
      return sizeof(value2);
      break;
    case VALUE_3:
      value3 = (uint32_t) read_num_bytes(data, sizeof(value3));
      return sizeof(value3);
      break;
    case VALUE_4:
      value4 = (uint64_t) read_num_bytes(data, sizeof(value4));
      return sizeof(value4);
      break;
    case VALUE_5:
      value5 = (uint64_t) read_num_bytes(data, sizeof(value5));
      return sizeof(value5);
      break;
    default:
      return 0;
  }
  */
  return 0;
}


// You must implement this function.
// It is called when the device receives a Device Data Update packet.
// Modifies data_update_buf to contain the parameter value.
//    param           -   Parameter index
//    data_update_buf -   buffer to return data in, little-endian
//    buf_len         -   Maximum length of the buffer
//
//    return          -   sizeof(param) on success; 0 otherwise

uint8_t device_read(uint8_t param, uint8_t* data_update_buf, size_t buf_len) {
  switch (param) 
  {
  	case ENABLE:

  	  break;
    case COMMAND_STATE: 
      break;
    case DUTY_CYCLE: 
      break;
    case PID_POS_SETPOINT: 
      break;
    case PID_POS_KP: 
      break;
    case PID_POS_KI: 
      break;
    case PID_POS_KD: 
      break;
    case PID_VEL_SETPOINT: 
      break;
    case PID_VEL_KP: 
      break;
    case PID_VEL_KI: 
      break;
    case PID_VEL_KD: 
      break;
    case CURRENT_THRESH: 
      break;
    case ENC_POS: 
      break;
    case ENC_VEL: 
      break;
    case MOTOR_CURRENT: 
      break;
    default:
      return 0;
    }
  /*
  switch (param) 
  {
    case VALUE_0:
      write_num_bytes(value0, data_update_buf, sizeof(value0));
      return sizeof(value0);
      break;
    case VALUE_1:
      write_num_bytes(value1, data_update_buf, sizeof(value1));
      return sizeof(value1);
      break;
    case VALUE_2:
      write_num_bytes(value2, data_update_buf, sizeof(value2));
      return sizeof(value2);
      break;
    case VALUE_3:
      write_num_bytes(value3, data_update_buf, sizeof(value3));
      return sizeof(value3);
      break;
    case VALUE_4:
      write_num_bytes(value4, data_update_buf, sizeof(value4));
      return sizeof(value4);
      break;
    case VALUE_5:
      write_num_bytes(value5, data_update_buf, sizeof(value5));
      return sizeof(value5);
      break;
    default:
      return 0;
  }
  */
  return 0;
}
