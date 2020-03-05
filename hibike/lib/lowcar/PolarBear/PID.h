#ifndef PID_h
#define PID_h

#include "Arduino.h"
#include <Encoder.h>

class PID
{
public:
	PID(double SetPoint, double KP, double KI, double KD, double initTime);
	double compute();
	void setCoefficients(double KP, double KI, double KD);
	void setSetpoint(double sd);
	double getKP();
	double getKI();
	double getKD();
	/* Below are functions for the encoder. */
	void updateEncoder();
	void encoderSetup();
	void resetEncoder();
	double readPos();
	double readVel();
	void updateVel();
	void updatePos();

private:
	double kp;
	double ki;
	double kd;
	double lastTime;
	double lastError;
	double setPoint;
	double errorSum;
	double prevPos;
	double prevVel;
	Encoder* enc;
};

#endif
