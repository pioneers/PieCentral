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
int delayMod = 1;
float dpwm_dt = 255 / 200000;


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

void change_pwm2(int current, int target, bool flip) {
	int pwm_difference;
        if (!flip) {
		pwm_difference = current - target;
		if (pwm_difference < 0) {
			pwm_difference *= -1;
		}
	} else {
		pwm_difference = (255 - current) + (255 - target);
	}
	float total_time = pwm_difference / dpwm_dt;
	int unit_delay = (int) (total_time / pwm_difference);
	if (!flip) {
		if (target > current) {
			for (; current < target; current++) {
				analogWrite(PWM2, current);
				delayMicroseconds(unit_delay);
			}
		} else {
			for (; current > target; current--) {
				analogWrite(PWM2, current);
				delayMicroseconds(unit_delay);
			}
		}
	} else {
		for (; current < 255; current++) {
			analogWrite(PWM2, current);
			delayMicroseconds(unit_delay);
		}
		if (invHigh) {
			digitalWrite(INV, LOW);
			invHigh = false;
		} else {
			digitalWrite(INV, HIGH);
			invHigh = true;
		}
		for (; current > target; current--) {
			analogWrite(PWM2, current);
			delayMicroseconds(unit_delay);
		}
	}
	currpwm2 = target;
}

//takes a value from -1 to 1 inclusive and writes to the motor and sets the PWM1 and PWM2 pins for direction
void drive(float target)
{
	if (target < -deadBand) {
		int goal = 255 + (int) (target * 255);
		change_pwm2(currpwm2, goal, !invHigh);
	} else if (target > deadBand) {
		target = target * -1;
		int goal = 255 + (int) (target * 255);
		change_pwm2(currpwm2, goal, invHigh);
	} else {
		change_pwm2(currpwm2, 255, false);
	}
}

void clearFault()
{
	analogWrite(PWM1, 255);
	analogWrite(PWM2, 255);
	currpwm2 = 255;
}

void setDeadBand(float range)
{
	deadBand = range;
}

float readDeadBand()
{
	return deadBand;
}
