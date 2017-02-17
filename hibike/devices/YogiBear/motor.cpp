#include "TimerOne.h"

#include "motor.h"
#include "pindefs.h"
//tab to handle all controls issued to the motor including driving and braking
void motorSetup() {
  pinMode(current_pin,INPUT);
  pinMode(INA, OUTPUT);
  pinMode(INB, OUTPUT);
  pinMode(enable_pin, OUTPUT);

  enable();  
  //pinMode(PWM, OUTPUT);
}

int readEnable() {
  return digitalRead(enable_pin);
}

void enable() {
  clearFault();
  digitalWrite(enable_pin, HIGH);
}

void disable() {
  digitalWrite(enable_pin, LOW);
}

//returns current in amps
float readCurrent() {
  return (analogRead(current_pin) - 3.7) / 30.2;
}

//takes a value from -1 to 1 inclusive and writes to the motor and sets the INA and INB pins for direction
void drive(float target) {
  
  if (target < 0) { 
    digitalWrite(INA, LOW);
    digitalWrite(INB, HIGH);
    target = target * -1;
  } else if (target > 0){
    digitalWrite(INA, HIGH);
    digitalWrite(INB, LOW);
  }

  Timer1.pwm(PWM, (int) (target * 1023));

}


void clearFault() {
  digitalWrite(INA, !digitalRead(INA));
  digitalWrite(INB, !digitalRead(INB));
  
  digitalWrite(INA, !digitalRead(INA));
  digitalWrite(INB, !digitalRead(INB));

  Timer1.pwm(PWM, 0);
  digitalWrite(enable_pin, LOW);
  digitalWrite(enable_pin, HIGH);
}


