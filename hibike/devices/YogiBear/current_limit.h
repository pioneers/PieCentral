#ifndef CURRENT_LIMIT_H
#define CURRENT_LIMIT_H
#include <stdint.h>

//function prototypes
void currentLimitSetup();
void timerOneOps();
void current_limiting();
void setCurrentThreshold(float x);
int read_limit_state();

extern uint8_t driveMode;
extern float pwmInput;
extern float pwmPID;
extern float current_threshold;
extern float pwmOutput;
extern unsigned long heartbeat;

#endif /* CURRENT_LIMIT_H */