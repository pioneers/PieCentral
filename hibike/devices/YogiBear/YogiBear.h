#ifndef YOGIBEAR_H
#define YOGIBEAR_H

#include "hibike_device.h" //to get the hibike framework

#define NUM_PARAMS 15
typedef enum {
  MANUALDRIVE = 0,
  PID_VEL = 1,
  PID_POS = 2
} DriveModes;

typedef enum {
  DUTY_CYCLE = 0,
  PID_POS_SETPOINT = 1,
  PID_POS_KP = 2,
  PID_POS_KI = 3,
  PID_POS_KD = 4,
  PID_VEL_SETPOINT = 5,
  PID_VEL_KP = 6,
  PID_VEL_KI = 7,
  PID_VEL_KD = 8,
  CURRENT_THRESH = 9,
  ENC_POS = 10,
  ENC_VEL = 11,
  MOTOR_CURRENT = 12,
  DEADBAND = 13
} param;


// function prototypes
void setup();
void loop();
float readPWMInput();
void resetPWMInput();
void resetDriveMode();
uint8_t readDriveMode();

#endif /* YOGIBEAR_H */
