#include <Encoder.h> //arduino Quadrature Encoder library with 4x sensing
#include <TimerThree.h> //Library for timer3

#include "encoder.h"
#include "pindefs.h"

//Code here that does position and velocity sensing
//This block of code is responsible for keeping track of the motor's position and velocity, without the say-so of any other blocks of code.

//Velocity sensing will have its own independent timer soley for its own use, and also use interupts.




Encoder myEnc(encoder0PinA, encoder0PinB);

// 2500/11 comes from 1000000 (1 sec) / 4400 (tick range)
long res = 100;
long interval_us = res*(2500/11); //interval in us

void encoderSetup(){
  
  pinMode(encoder0PinA,INPUT);
  pinMode(encoder0PinB,INPUT);

  Timer3.initialize(interval_us);
  Timer3.attachInterrupt(timerThreeOps);
}

void timerThreeOps() {
  velocity();
}

double encoder(){
  return myEnc.read();
}

void velocity(){
  double enc_reading = encoder();
  vel = ((enc_reading - old_encoder0Pos)*1000000)/((float) interval_us);
  old_encoder0Pos = enc_reading; //calculate for the next vel calc
}

void position() {
  pos = encoder();
}

