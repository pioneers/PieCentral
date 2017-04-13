#include "YogiBear.h"
#include "pid.h"
#include "encoder.h"
#include "current_limit.h"
#include "motor.h"
#include "LED.h"

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
YOGI_BEAR,                      // Device Type
0x01,                      // Year
UID_RANDOM,     // ID
};
///////////////////////////////////////////////

//A space for constants.
float pwmInput = 0; //Value that is received from hibike and is the goal PWM
uint8_t driveMode = 0; 

void setup() {
  motorSetup();
  currentLimitSetup();
  encoderSetup();
  PIDSetup();
  setup_LEDs();
  test_LEDs();
  hibike_setup(); //use default heartbeat rates. look at /lib/hibike/hibike_device.cpp for exact values
  motorDisable();
  driveMode = MANUALDRIVE;
}

void loop() {
  ctrl_LEDs();
  hibike_loop();

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
  switch (param) {

    case DUTY_CYCLE:
      motorEnable();
      disablePID();
      driveMode = MANUALDRIVE;
      pwmInput = ((float *)data)[0];
      return sizeof(float);
      break;

    case PID_POS_SETPOINT: 
      motorEnable();
      driveMode = PID_POS;
      enablePos();
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
      motorEnable(); 
      driveMode = PID_VEL;
      enableVel();
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
        resetEncoder();
        return sizeof(float);
      }

      break;

    case ENC_VEL: 
      break;

    case MOTOR_CURRENT: 
      break;

    case DEADBAND:
      setDeadBand(((float *)data)[0]);
      return sizeof(float);
      break;

    default:
      return 0;
  }

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
  float* float_buf;

  switch (param) {

    case DUTY_CYCLE: 
      if(buf_len < sizeof(float)) {
        return 0;
      }
      float_buf = (float *) data_update_buf;
      float_buf[0] = readPWMInput();
      return sizeof(float);
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
      if(buf_len < sizeof(float)) {
        return 0;
      }
      float_buf = (float *) data_update_buf;
      float_buf[0] = readPos();
      return sizeof(float);
      break;

    case ENC_VEL: 
      if(buf_len < sizeof(float)) {
        return 0;
      }
      float_buf = (float *) data_update_buf;
      float_buf[0] = readVel();
      return sizeof(float);
      break;

    case MOTOR_CURRENT: 
      if(buf_len < sizeof(float)) {
        return 0;
      }
      float_buf = (float *) data_update_buf;
      float_buf[0] = readCurrent();
      return sizeof(float);
      break;

    case DEADBAND:
      if(buf_len< sizeof(float)){
        return 0;
      }
      float_buf = (float *) data_update_buf;
      float_buf[0] = readDeadBand();
      return sizeof(float);
      break;

    default:
      return 0;
      break;
  }

  return 0;
}


float readPWMInput() {
  return pwmInput;
}

void resetPWMInput() {
	pwmInput = 0;
}

uint8_t readDriveMode() {
  return driveMode;
}

void resetDriveMode() {
  driveMode = MANUALDRIVE;
}

// You must implement this function.
// It is called when the BBB sends a message to the Smart Device tellinng the Smart Device to disable itself.
// Consult README.md, section 6, to see what exact functionality is expected out of disable.
void device_disable() {
  motorDisable();
}
