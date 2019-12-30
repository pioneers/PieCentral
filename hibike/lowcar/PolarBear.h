#ifndef POLARBEAR_H
#define POLARBEAR_H

#include "Device.h"
#include "defs.h"

class PolarBear : public Device
{
public:
  PolarBear ();
  virtual uint8_t PolarBear::device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len);
  virtual uint32_t PolarBear::device_write (uint8_t param, uint8_t *data_buf);
  void PolarBear::device_enable ();
  void PolarBear::device_disable ();
  void PolarBear::device_actions ();

  #define NUM_PARAMS 15
  typedef enum {
    MANUALDRIVE = 0,
    PID_VEL = 1,
    PID_POS = 2
  } DriveModes;

  typedef enum {
    DUTY_CYCLE = 0,
    PID_POS_SETPOINT = 1,
    PID_POS_KP = 2,
    PID_POS_KI = 3,
    PID_POS_KD = 4,
    /**PID_VEL_SETPOINT = 5,
    PID_VEL_KP = 6,
    PID_VEL_KI = 7,
    PID_VEL_KD = 8, */
    CURRENT_THRESH = 9,
    ENC_POS = 10,
    ENC_VEL = 11,
    MOTOR_CURRENT = 12,
    DEADBAND = 13,
    MOTOR_ENABLED = 14, // Added for lowcar; only in DEVICE_READ (not write)
    PWM_INPUT = 15, // Lowcar to get rid of read/reset PWMInput
    DRIVE_MODE = 16 // Lowcar to get rid of read/reset drive mode
  } param;
private:
  float pwmInput;
  uint8_t driveMode;
  bool motorEnabled;
  float deadBand;
  int currpwm1;
  int currpwm2;
  int delayMod;
  float dpwm_dt;
  Messenger msgr;
  Encoder encdr;
  PID pid;
  void drive(float target);
};



// function prototypes
//void setup();
//void loop();
/* Moved to device read/write
float readPWMInput();
void resetPWMInput();
void resetDriveMode();
uint8_t readDriveMode();
*/

// ****************
// FROM OLD MOTOR.H
// ****************


//function prototypes
//void motorSetup(); Moved to device_enable
//void motorEnable(); Moved to device_enable
//void motorDisable(); Moved to device_disable
//bool isMotorEnabled(); Moved to device_read

//returns current in amps
//float readCurrent(); moved to device_read

//takes a value from -1 to 1 inclusive and writes to the motor and sets the INA and INB pins for direction
//void drive(float target);
//void clearFault(); lowcar: current limiting moved
//void setDeadBand(float range); moved to device_write
//float readDeadBand(); moved to device_read

#endif /* POLARBEAR_H */
