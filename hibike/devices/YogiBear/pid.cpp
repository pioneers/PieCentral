#include <PID_v1.h>

#include "pid.h"
//double x = 2.0;

//PID positionControl(&x, &x, &x, x, x, x, DIRECT);
PID positionControl(&pos, &pwmPID, &PIDPos, PIDPosKP, PIDPosKI, PIDPosKD, DIRECT);
PID velocityControl(&vel, &pwmPID, &PIDVel, PIDVelKP, PIDVelKI, PIDVelKD, DIRECT);

void PIDSetup() {
  positionControl.SetOutputLimits(-1, 1);
  positionControl.SetSampleTime(20);
  velocityControl.SetOutputLimits(-1, 1);
  velocityControl.SetSampleTime(20);
}

void enablePos() {
  positionControl.SetMode(AUTOMATIC);
  velocityControl.SetMode(MANUAL);
}

void enableVel() {
  positionControl.SetMode(MANUAL);
  velocityControl.SetMode(AUTOMATIC);
}

void disablePID() {
  positionControl.SetMode(MANUAL);
  velocityControl.SetMode(MANUAL);
}

void updatePosPID() {
  positionControl.SetTunings(PIDPosKP, PIDPosKI, PIDPosKD);
}

void updateVelPID() {
  velocityControl.SetTunings(PIDVelKP, PIDVelKI, PIDVelKD);
}

void posPID() {
  positionControl.Compute();
}

void velPID() {
  velocityControl.Compute();
}

