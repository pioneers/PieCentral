#ifndef PID_H
#define PID_H


// function prototypes
void PIDSetup();
void timerTwoOps();
void enablePos();
void enableVel();
void disablePID();
void updatePosPID();
void updateVelPID();
void posPID();
void velPID();
void setPosSetpoint(float x);
void setPosKP(float x);
void setPosKI(float x);
void setPosKD(float x);
void setVelSetpoint(float x);
void setVelKP(float x);
void setVelKI(float x);
void setVelKD(float x);

extern double pos;
extern double vel;
extern uint8_t driveMode;

/*
float PIDPos;
float PIDPosKP;
float PIDPosKI;
float PIDPosKD;

float PIDVel;
float PIDVelKP;
float PIDVelKI;
float PIDVelKD;

float pwmPID;
*/

#endif /* PID_H */