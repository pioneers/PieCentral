#ifndef PID_H
#define PID_H


// function prototypes
void PIDSetup();
void enablePos();
void enableVel();
void disablePID();
void updatePosPID();
void updateVelPID();
void posPID();
void velPID();


extern double PIDPos;
extern double PIDPosKP;
extern double PIDPosKI;
extern double PIDPosKD;

extern double PIDVel;
extern double PIDVelKP;
extern double PIDVelKI;
extern double PIDVelKD;

extern double pos;
extern double pwmPID;
extern double vel;
extern double pwmPID;


#endif /* PID_H */