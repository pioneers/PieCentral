#include "YogiBear.h"
#include "ui.h"
#include "pid.h"
#include "encoder.h"
#include "current_limit.h"
#include "motor.h"

//A space for constants.
float pwmInput = 0; //Value that is received from hibike and is the goal PWM
uint8_t driveMode = 0; //0 for manual, 1 for PID Velocity, 2 for PID Position
bool enabled = false;

double pos = 0; //these both used to be volatile, but PID library doesn't convert well between volatiles and not-volatiles in c++
double vel = 0;

bool hibike = true;
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
	  	if (data[0] == 0) {
	  		enabled = false;
	  		disable();
	  	} else {
	  		enabled = true;
	  		enable();
	  	}
      return sizeof(uint8_t);
  	  break;
    case COMMAND_STATE: 
    	driveMode = data[0];
    	if (driveMode == 0) {
    		disablePID();
    	} else if (driveMode == 1) {
    		enableVel();
    	} else {
    		enablePos();
    	}
      return sizeof(driveMode);
      break;
    case DUTY_CYCLE: 
    	pwmInput = ((float *)data)[0];
      return sizeof(float);
      break;
    case PID_POS_SETPOINT: 
    	setPosSetpoint(((float *)data)[0]);
      return sizeof(float);
      break;
    case PID_POS_KP: 
    	setPosKP(((float *)data)[0]);
      return sizeof(float);
      break;
    case PID_POS_KI: 
    	setPosKI(((float *)data)[0]);
      return sizeof(float);
      break;
    case PID_POS_KD: 
    	setPosKD(((float *)data)[0]);
      return sizeof(float);
      break;
    case PID_VEL_SETPOINT: 
    	setVelSetpoint(((float *)data)[0]);
      return sizeof(float);
      break;
    case PID_VEL_KP: 
    	setVelKP(((float *)data)[0]);
      return sizeof(float);
      break;
    case PID_VEL_KI: 
    	setVelKI(((float *)data)[0]);
      return sizeof(float);
      break;
    case PID_VEL_KD: 
    	setVelKD(((float *)data)[0]);
      return sizeof(float);
      break;
    case CURRENT_THRESH: 
    	setCurrentThreshold(((float *)data)[0]);
      return sizeof(float);
      break;
    case ENC_POS: 
    	if((float) data[0] == 0) {
    		zeroEncoder();
      return sizeof(float);
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
//    return          -   sizeof(value) on success; 0 otherwise

uint8_t device_read(uint8_t param, uint8_t* data_update_buf, size_t buf_len) {
  double reading;
  float* float_buf;
  switch (param) 
  {
  	case ENABLE:
  	  data_update_buf[0] = enabled;
  	  return sizeof(uint8_t);
  	  break;
    case COMMAND_STATE: 
      data_update_buf[0] = driveMode;
      return sizeof(driveMode);
      break;
    case DUTY_CYCLE: 
      float_buf = (float *) data_update_buf;
      float_buf[0] = pwmInput;
      return sizeof(pwmInput);
      break;
    case PID_POS_SETPOINT: 
      float_buf = (float *) data_update_buf;
      float_buf[0] = PIDPos;
      return sizeof(float);
      break;
    case PID_POS_KP: 
      float_buf = (float *) data_update_buf;
      float_buf[0] = PIDPosKP;
      return sizeof(float);
      break;
    case PID_POS_KI:
      float_buf = (float *) data_update_buf;
      float_buf[0] = PIDPosKI;
      return sizeof(float); 
      break;
    case PID_POS_KD: 
      float_buf = (float *) data_update_buf;
      float_buf[0] = PIDPosKD;
      return sizeof(float);
      break;
    case PID_VEL_SETPOINT: 
      float_buf = (float *) data_update_buf;
      float_buf[0] = PIDVel;
      return sizeof(float);
      break;
    case PID_VEL_KP: 
      float_buf = (float *) data_update_buf;
      float_buf[0] = PIDVelKP;
      return sizeof(float);
      break;
    case PID_VEL_KI: 
      float_buf = (float *) data_update_buf;
      float_buf[0] = PIDVelKI;
      return sizeof(float);
      break;
    case PID_VEL_KD: 
      float_buf = (float *) data_update_buf;
      float_buf[0] = PIDVelKD;
      return sizeof(float);
      break;
    case CURRENT_THRESH: 
      float_buf = (float *) data_update_buf;
      float_buf[0] = current_threshold;
      return sizeof(float);
      break;
    case ENC_POS: 
      float_buf = (float *) data_update_buf;
      float_buf[0] = readPos();
      return sizeof(float);
      break;
    case ENC_VEL: 
      float_buf = (float *) data_update_buf;
      float_buf[0] = readVel();
      return sizeof(float);
      break;
    case MOTOR_CURRENT: 
      float_buf = (float *) data_update_buf;
      float_buf[0] = readCurrent();
      return sizeof(float);
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
