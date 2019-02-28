#ifndef CURRENT_LIMIT_H
#define CURRENT_LIMIT_H
#include <stdint.h>

//function prototypes
void currentLimitSetup();
void setCurrentThreshold(float x);
int read_limit_state();

void ctrl_pwm();

#endif /* CURRENT_LIMIT_H */
