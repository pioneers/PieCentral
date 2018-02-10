#include "TimerOne.h"
#include "motor.h"
#include "pindefs.h"
#include "YogiBear.h"
#include "pid.h"
#include "encoder.h"

//tab to handle all controls issued to the motor including driving and braking

bool motorEnabled = false;
float deadBand = 0.05;

void motorSetup() {
  pinMode(current_pin,INPUT);
  pinMode(INA, OUTPUT);
  pinMode(INB, OUTPUT);

  motorEnable();
  //pinMode(PWM, OUTPUT);
}

void motorEnable() {
  clearFault();
  pinMode(enable_pin, INPUT); //pin is pulled up, so put in high impedance state instead of writing high
  motorEnabled = true;
}

void motorDisable() {
  pinMode(enable_pin, OUTPUT);
  digitalWrite(enable_pin, LOW);
  disablePID();
  resetPID();
  resetEncoder();
  resetPWMInput();
  resetDriveMode();
  motorEnabled = false;
}

bool isMotorEnabled() {
  return motorEnabled;
}

//returns current in amps
float readCurrent() {
  return (analogRead(current_pin) / 33.0); //Number was generated based on a few tests across multiple boards. Valid for majority of good boards
}

//takes a value from -1 to 1 inclusive and writes to the motor and sets the INA and INB pins for direction
void drive(float target) {

  if (target < -deadBand) {
    digitalWrite(INA, LOW);
    digitalWrite(INB, HIGH);
    target = target * -1;
  } else if (target > deadBand) {
    digitalWrite(INA, HIGH);
    digitalWrite(INB, LOW);
  } else {
    target = 0;
  }

  Timer1.pwm(PWM, (int) (target * 1023));

}


void clearFault() {
  digitalWrite(INA, !digitalRead(INA));
  digitalWrite(INB, !digitalRead(INB));

  digitalWrite(INA, !digitalRead(INA));
  digitalWrite(INB, !digitalRead(INB));

  Timer1.pwm(PWM, 0);
  pinMode(enable_pin, OUTPUT);
  digitalWrite(enable_pin, LOW);
  pinMode(enable_pin, INPUT);
}

void setDeadBand(float range) {
  deadBand = range;
}

float readDeadBand() {
  return deadBand;
}
