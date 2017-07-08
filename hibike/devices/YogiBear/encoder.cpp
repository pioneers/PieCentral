/* Licensed to Pioneers in Engineering under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Pioneers in Engineering licenses
 * this file to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 *  with the License.  You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 */ under the License
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
double pos = 0;
double vel = 0;
volatile signed long old_encoder0Pos = 0;

void timerThreeOps() {
  updatePos();
  updateVel();
}

void encoderSetup() {
  
  pinMode(encoder0PinA,INPUT);
  pinMode(encoder0PinB,INPUT);

  Timer3.initialize(interval_us);
  Timer3.attachInterrupt(timerThreeOps);
}

void resetEncoder() {
  myEnc.write(0);
}

void updatePos() {
  pos = myEnc.read();
}

double readPos() {
  return pos;
}

double readVel() {
  return vel;
}

void updateVel() {
  double enc_reading = pos;
  vel = ((enc_reading - old_encoder0Pos)*1000000)/((float) interval_us);
  old_encoder0Pos = enc_reading; //calculate for the next vel calc
}
