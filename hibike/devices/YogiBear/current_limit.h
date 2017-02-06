#ifndef CURRENT_LIMIT_H
#define CURRENT_LIMIT_H

//function prototypes
void currentLimitSetup();
void timerOneOps();
void current_limiting();

extern int driveMode;
extern double pwmInput;
extern double pwmPID;
extern float current_threshold;
extern float pwmOutput;
extern unsigned long heartbeat;

#endif /* CURRENT_LIMIT_H */