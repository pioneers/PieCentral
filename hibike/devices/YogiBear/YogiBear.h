#ifndef YOGIBEAR_H
#define YOGIBEAR_H

#include "hibike_device.h" //to get the hibike frameworkd

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  YOGI_BEAR,                      // Device Type
  0x01,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////



#define NUM_PARAMS 15

typedef enum {
  ENABLE = 0,
  COMMAND_STATE = 1,
  DUTY_CYCLE = 2,
  PID_POS_SETPOINT = 3,
  PID_POS_KP = 4,
  PID_POS_KI = 5,
  PID_POS_KD = 6,
  PID_VEL_SETPOINT = 7,
  PID_VEL_KP = 8,
  PID_VEL_KI = 9,
  PID_VEL_KD = 10,
  CURRENT_THRESH = 11,
  ENC_POS = 12,
  ENC_VEL = 13,
  MOTOR_CURRENT = 14
} param;


// function prototypes
void setup();
void loop();



#endif /* YOGIBEAR_H */
