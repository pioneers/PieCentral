#include <TimerOne.h> //arduino libraries go in <
#include "current_limit.h"
#include "motor.h" //our own motor.h
#include "YogiBear.h"
#include "pid.h"

//code that does current limiting.
//This will be called every time the motor controller decides to adjust the PWM to the motor.

int pwm_sign = 1; //separates the sign from the PWM value
float pwmOutput = 0; //Value controlled by current limiting and is what is written to the motor
float current_threshold = 3.0; //threshold in amps
#define LIMITED 4 //when in the limit state PWM = PWM/LIMITED

#define EXIT_MAX 250 //how many ms we want to be in CAUGHT_MAX before moving onto LIMIT state 
#define EXIT_LIMIT 1000 //how many ms we want to be in LIMIT before moving onto SPIKE state
#define EXIT_SPIKE 500 //how many ms we want to be in SPIKE before moving onto either the STANDARD or LIMIT state

int in_max = 0; //how many times we have been in the CAUGHT_MAX state
int above_threshold = 0;
int in_limit = 0; //how many times we have been in the LIMIT state
int in_spike = 0; //how many times we have been in the SPIKE state
int below_threshold = 0; 

int limit_state = 0;

//FSM STATES
typedef enum {
  STANDARD = 0,
  CAUGHT_MAX = 1,
  LIMIT = 2,
  SPIKE = 3
} limitState;


void current_limiting() {
  float targetPWM;
  uint8_t driveMode = readDriveMode();
  
  if (driveMode == MANUALDRIVE) {
    targetPWM = readPWMInput();
  } else if (driveMode == PID_POS || driveMode == PID_VEL) {
    targetPWM = readPWMPID();
  }
  
  float current_read = readCurrent(); 
  
  if (targetPWM < 0) { //separate the sign to make calculations easier, we only care about magnitude
    pwm_sign = -1;
    targetPWM = targetPWM * -1;
  } else {
    pwm_sign = 1;
  }

  switch(limit_state) {
    
    case STANDARD: //we allow the pwm to be passed through normally and check to see if the CURRENT ever spikes above the threshold
      if (current_read > current_threshold) {
        limit_state = CAUGHT_MAX;
      } else {
        if (above_threshold > 0) {
          above_threshold--;
        }
      }
      break;
      
    case CAUGHT_MAX: //we have seen the max and we check to see if we are above max for EXIT_MAX consecutive cycles and then we go to LIMIT to protect the motor
      if (in_max > EXIT_MAX) {
        if(above_threshold >= EXIT_MAX / 2) {
          above_threshold = 0;
          limit_state = LIMIT;
        } else {
          limit_state = STANDARD;
        }
        in_max = 0;
      }

      if (current_read > current_threshold) {
        above_threshold++;
      }
      in_max++;
      break;
      
    case LIMIT: //we limit the pwm to 0.25 the value and wait EXIT_LIMIT cycles before attempting to spike and check the current again
      targetPWM = targetPWM / LIMITED;
      if (in_limit > EXIT_LIMIT) {
        in_limit = 0;
        limit_state = SPIKE;
      } else {
        in_limit++;
      }
      break;
      
    case SPIKE: //we bring the pwm back to the target for a brief amount of time and check to see if it can continue in standard or if we need to continue limiting
      if (in_spike > EXIT_SPIKE) {
        if (below_threshold >= (EXIT_SPIKE/100)*99) {
          limit_state = STANDARD;
        } else {
          limit_state = LIMIT;
        }
        below_threshold = 0;
        in_spike = 0;
      } else {
        if (current_read < current_threshold) {
          below_threshold++;
        }
        in_spike++;
      }
      break;
  }
  pwmOutput = targetPWM * pwm_sign;
}

void timerOneOps() {
  current_limiting();
  drive(pwmOutput);
}

void currentLimitSetup() {
  Timer1.initialize(1000);
  Timer1.attachInterrupt(timerOneOps);
}

void setCurrentThreshold(float x) {
  current_threshold = x;
}

int read_limit_state() {
  return limit_state;
}



