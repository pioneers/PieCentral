#ifndef CURRENT_LIMIT_H
#define CURRENT_LIMIT_H

//function prototypes
void currentLimitSetup();
void timerOneOps();
void current_limiting();
void setCurrentThreshold(float x);

extern uint8_t driveMode;
extern float pwmInput;
extern float pwmPID;
extern float current_threshold;
extern float pwmOutput;
extern unsigned long heartbeat;

#endif /* CURRENT_LIMIT_H */