#ifndef MOTOR_H
#define MOTOR_H

//function prototypes
void motorSetup();

void motorEnable();

void motorDisable();

bool readMotorEnabled();

//returns current in amps
float readCurrent();

//takes a value from -1 to 1 inclusive and writes to the motor and sets the INA and INB pins for direction
void drive(float target);
void clearFault();

#endif /* MOTOR_H */