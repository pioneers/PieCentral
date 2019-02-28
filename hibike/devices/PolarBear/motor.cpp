#include "TimerOne.h"
#include "motor.h"
#include "pindefs.h"
#include "PolarBear.h"
#include "pid.h"
#include "encoder.h"

//tab to handle all controls issued to the motor including driving and braking

bool motorEnabled = false;
float deadBand = 0.05;

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
		digitalWrite(INV, LOW);
		analogWrite(PWM1, 255);
		analogWrite(PWM2, 255 + (int) (target * 255));
	} else if (target > deadBand) {
		target = target * -1;
		digitalWrite(INV, HIGH);
		analogWrite(PWM1, 255);
		analogWrite(PWM2, 255 + (int) (target * 255));
	} else {
		analogWrite(PWM2, HIGH);
		analogWrite(PWM1, HIGH);
	}
}


void clearFault() 
{
	analogWrite(PWM1, 255);
	analogWrite(PWM2, 255);
}

void setDeadBand(float range) 
{
	deadBand = range;
}

float readDeadBand() 
{
	return deadBand;
}
