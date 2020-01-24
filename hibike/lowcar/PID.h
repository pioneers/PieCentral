#ifndef PID_h
#define PID_h

#include "Arduino.h"
#include <Encoder.h>

class PID
{
public:
	PID(double SetPoint, double KP, double KI, double KD, double initTime, Encoder* encoder);
	double compute();
	void setCoefficients(double KP, double KI, double KD);
	void setSetpoint(double sd);
	double getKP();
	double getKI();
	double getKD();

private:
	double kp;
	double ki;
	double kd;
	double lastTime;
	double lastError;
	double setPoint;
	double errorSum;
	Encoder* enc;
};

#endif
