#include "PID.h"

#define encoder0PinA	14
#define encoder0PinB	15

PID::PID(double SetPoint, double KP, double KI, double KD, double initTime):
	enc(encoder0PinA, encoder0PinB)
{
	kp = KP;
	ki = KI;
	kd = KD;
	setPoint = SetPoint;
	lastTime = initTime;
	enc->write(0); //reset the encoder because why not
	prevPos = enc->read();
	prevVel = 0.0;
}

/* Computes a value between -1 and 1 inclusive to tell how to
** adjust the motor controller pins.
** This is called continually by PolarBear.
** Also updates the encoder position and velocity with each call. */
double PID::compute()
{
	//updateVel();
	double currTime = (double)(millis());
	double deltaTime = currTime - lastTime;


	//double goalPos = prevPos + (prevVel + setPoint)*(deltaTime) / 2
	//double error = goalPos - enc->read();	//uses encoder reading as current position
	double error = setPoint - enc->read();	//uses encoder reading as current position


	errorSum += error * deltaTime;
	double deriv = (error - lastError) / deltaTime;
	lastTime = currTime;
	double out = kp * error + ki * errorSum + kd * deriv;


	prevPos = enc->read();
	//prevVel = setPoint;
	if (out > 1)
	{
		return 1;
	}
	else if (out < -1)
	{
		return -1;
	}
	return out;
}

void PID::setCoefficients(double KP, double KI, double KD)
{
	kp = KP;
	ki = KI;
	kd = KD;
}

void PID::setSetpoint(double sp) { setPoint = sp; }

double PID::getKP() { return kp; }
double PID::getKI() { return ki; }
double PID::getKD() { return kd; }

double PID::readPos() { return enc->read(); }
double PID::readVel() { return 0.00; }

/****************************************************
* 				ENCODER FUNCTIONS
****************************************************/
long res = 100;
long interval_us = res*(2500/11); //interval in us; 2500/11 == 1000000 (1 sec) / 4400 (tick range)

void PID::encoderSetup() {
  pinMode(encoder0PinA,INPUT);
  pinMode(encoder0PinB,INPUT);
}

void PID::resetEncoder() {
  enc->write(0);
}

// Updates the encoder's velocity by calculating the position slope.
void PID::updateVel() {
  double enc_reading = enc->read();
  prevVel = ((enc_reading - prevPos)*1000000)/((float) interval_us);
  prevPos = enc_reading; // Save the current pos
}

/**************
Original Encoder
**************/
/*
long res = 100;
long interval_us = res*(2500/11); //interval in us; 2500/11 == 1000000 (1 sec) / 4400 (tick range)
double pos = 0;
double vel = 0;
volatile signed long old_encoder0Pos = 0;

void PID::updateEncoder() {
  updatePos();
  updateVel();
}

void PID::encoderSetup() {
  pinMode(encoder0PinA,INPUT);
  pinMode(encoder0PinB,INPUT);
}

void PID::resetEncoder() {
  enc->write(0);
}

double PID::readPos() {
  return pos;
}

double PID::readVel() {
  return vel;
}

void PID::updatePos() {
  pos = enc->read();
}
*/
