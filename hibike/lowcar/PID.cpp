#include "PID.h"

PID::PID(double SetPoint, double KP, double KI, double KD, double initTime, Encoder* encoder):
	enc(encoder)
{
	kp = KP;
	ki = KI;
	kd = KD;
	setPoint = SetPoint;
	lastTime = initTime;
}

//very cool code :))))
double PID::compute()
{
	double currTime = (double)(millis());
	double deltaTime = currTime - lastTime;
	double error = setPoint - enc->read();	//uses encoder reading as current position
	errorSum += error * deltaTime;
	double deriv = (error - lastError) / deltaTime
	lastTime = currTime;
	double out = kp * error + ki * errorSum + kd * deriv;
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
