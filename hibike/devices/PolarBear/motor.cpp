#include "TimerOne.h"
#include "motor.h"
#include "pindefs.h"
#include "PolarBear.h"
#include "pid.h"
#include "encoder.h"

//tab to handle all controls issued to the motor including driving and braking

bool motorEnabled = false;
float deadBand = 0.05;
bool invHigh = false;
int currpwm1 = 0;
int currpwm2 = 0;

void motorSetup() 
{
	pinMode(feedback,INPUT);
	pinMode(PWM1, OUTPUT);
	pinMode(PWM2, OUTPUT);
	pinMode(INV, OUTPUT);
	digitalWrite(INV, LOW);

	motorEnable();
}

void motorEnable() 
{
	clearFault();
	motorEnabled = true;
}

void motorDisable() 
{
	disablePID();
	resetPID();
	resetEncoder();
	resetPWMInput();
	resetDriveMode();
	motorEnabled = false;
}

bool isMotorEnabled() 
{
	return motorEnabled;
}

//returns current in amps
float readCurrent() 
{
	return (analogRead(feedback) / 0.0024); //Number was generated based on a few tests across multiple boards. Valid for majority of good boards
}

//takes a value from -1 to 1 inclusive and writes to the motor and sets the PWM1 and PWM2 pins for direction
void drive(float target) 
{
	if (target < -deadBand) {
		int target = 255 + (int) (target * 255);
		change_pwm2(currpwm2, target, !invHigh);
	} else if (target > deadBand) {
		target = target * -1;
		int target = 255 + (int) (target * 255);
		change_pwm2(currpwm2, target, invHigh);
	} else {
		change_pwm2(currpwm2, 255, false);
	}
}

void change_pwm2(int current, int target, bool flip) {
	if (!flip) {
		if (target > current) {
			for (current < target; current++) {
				analogWrite(PWM2, current);
				if (current % 4 == 0) {
					delay(1);
				}
			}
		} else {
			for (current > target; current--) {
				analogWrite(PWM2, current);
				if (current % 4 == 0) {
					delay(1);
				}
			}
		}
	} else {
		for (current > 0; current--) {
			analogWrite(PWM2, current);
			if (current % 4 == 0) {
				delay(1);
			}
		}
		if (invHigh) {
			digitalWrite(INV, LOW);
			invHigh = false;
		} else {
			digitalWrite(INV, HIGH);
			invHigh = true;
		}
		for (current < target, current++) {
			analogWrite(PWM2, current);
			if (current % 4 == 0) {
				delay(1);
			}
		}
	}
	currpwm2 = target;
}


void clearFault() 
{
	analogWrite(PWM1, 255);
	analogWrite(PWM2, 255);
	pwm2curr = 255;
}

void setDeadBand(float range) 
{
	deadBand = range;
}

float readDeadBand() 
{
	return deadBand;
}
