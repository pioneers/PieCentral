#ifndef ENCODER_H
#define ENCODER_H

//function prototypes
void encoderSetup();
void timerThreeOps();
double encoder();
void velocity();
void position();
void zeroEncoder();
void updateVel();
void updatePos();
double readPos();
double readVel();

extern double pos;
extern double vel;
extern volatile signed long old_encoder0Pos;


#endif /* ENCODER_H */