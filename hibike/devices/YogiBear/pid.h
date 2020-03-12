#ifndef PID_H
#define PID_H


// function prototypes
void PIDSetup();
float readPWMPID();
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
void resetPID();

#endif /* PID_H */
