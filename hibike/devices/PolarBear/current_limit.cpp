#include <TimerOne.h> //arduino libraries go in <
#include "current_limit.h"
#include "motor.h" //our own motor.h
#include "PolarBear.h"
#include "pid.h"

//code that does current limiting.
//This will be called every time the motor controller decides to adjust the PWM to the motor.

float current_threshold = 5.0; //threshold in amps
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


void setCurrentThreshold(float x) 
{
	current_threshold = x;
}

int read_limit_state() 
{
	return limit_state;
}

// takes the desired PWM input, then decides whether to limit the current outputs the PWM output actually written to the motor
int current_limiting (float pwm_in) {
	
	int pwm_sign = (pwm_in > 0) ? 1 : -1; //separate the sign to make calculations easier, we only care about magnitude
	pwm_in *= (float) pwm_sign;
	
	float current_read = readCurrent(); 

	switch (limit_state) {
		
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
			pwm_in /= LIMITED;
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
	return pwm_in * pwm_sign; //returned signed and (possibly) limited pwm_input
}

/*
void timerOneOps() {
  current_limiting();
  drive(pwmOutput);
}

void currentLimitSetup() {
  Timer1.initialize(1000);
  Timer1.attachInterrupt(timerOneOps);
}
*/

void ctrl_pwm()
{
	uint8_t drive_mode = readDriveMode();
	float pwm_in = (drive_mode == MANUALDRIVE) ? readPWMInput() : readPWMPID();
	//float pwm_out = current_limiting(pwm_in);
	float pwm_out = pwm_in;
	drive(pwm_out);
}
