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



#define NUM_PARAMS 14

typedef enum {
  COMMAND_STATE = 0,
  DUTY_CYCLE = 1,
  PID_POS_SETPOINT = 2,
  PID_POS_KP = 3,
  PID_POS_KI = 4,
  PID_POS_KD = 5,
  PID_VEL_SETPOINT = 6,
  PID_VEL_KP = 7,
  PID_VEL_KI = 8,
  PID_VEL_KD = 9,
  CURRENT_THRESH = 10,
  ENC_POS = 11,
  ENC_VEL = 12,
  MOTOR_CURRENT = 13
} param;


// function prototypes
void setup();
void loop();

void timerTwoOps();


#endif /* YOGIBEAR_H */
