#include "PolarBear.h"
#include "pid.h"
#include "encoder.h"
#include "LED.h"
#include "pindefs.h"
#include <cstdlib> // For abs() in drive()

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
	POLAR_BEAR,     // Device Type
	0x01,           // Year
	UID_RANDOM,     // ID
};
///////////////////////////////////////////////

PolarBear::PolarBear () : Device (DeviceID::POLAR_BEAR, 2),  encdr(encoder0PinA, encoder0PinB), msngr(), pid(0, 0, 0, 0, millis(), encdr)
{
	this.pwmInput = 0; // Setpoint to be used with PID
	this.driveMode = 0;
	this.motorEnabled = false;
	this.deadBand = 0.05;
	this.currpwm1 = 255;
	this.currpwm2 = 255;
	this.delayMod = 1;
	this.dpwm_dt = 255 / 200000;
}

// You must implement this function.
// It is called when the device receives a Device Data Update packet.
// Modifies data_buf to contain the parameter value.
//    param           -   Parameter index
//    data_buf        -   buffer to return data in, little-endian
//    buf_len         -   Maximum length of the buffer
//
//    return          -   sizeof(value) on success; 0 otherwise
uint8_t PolarBear::device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len)
{
  float* float_buf;
	double* double_buf;
	boolean* boolean_buf;

	switch (param) {

		case DUTY_CYCLE:
			if(buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this.pwmInput; // Same as devie_read on PWMINPUT
			return sizeof(float);
			break;

		case PID_POS_SETPOINT:
			break;

		case PID_POS_KP:
			break;

		case PID_POS_KI:
			break;

		case PID_POS_KD:
			break;

		case CURRENT_THRESH:
			break;

		case ENC_POS:
			if (buf_len < sizeof(double)) {
				return 0;
			}
			double_buf = (double *) data_buf;
			double_buf[0] = this.encdr.readPos();
			return sizeof(double);
			break;

		case ENC_VEL:
			if (buf_len < sizeof(double)) {
				return 0;
			}
			double_buf = (double *) data_buf;
			double_buf[0] = this.encdr.readVel();
			return sizeof(double);
			break;

		case MOTOR_CURRENT:
			if (buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = (analogRead(feedback) / 0.0024); //feedback def in pindefs.h
			return sizeof(float);
			break;

		case DEADBAND:
			if (buf_len< sizeof(float)){
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this.deadBand;
			return sizeof(float);
			break;

		case MOTOR_ENABLED: // Lowcar: Reads whether or not motor is enabled.
			if (buf_len < sizeof(boolean)) {
				return 0;
			}
			boolean_buf = (boolean *) data_buf;
			boolean_buf[0] = this.motorEnabled;
			return sizeof(boolean);
			break;

		case PWM_INPUT: // Lowcar: Replacement for readPWMInput
			if (buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this.pwmInput;
			return sizeof(float);
			break;

		case DRIVE_MODE: // Lowcar: Replacement for readDriveMode
			if (buf_len < sizeof(uint8_t)) {
				return 0;
			}
			data_buf[0] = this.driveMode
			return sizeof(uint8_t);
			break;

		default:
			return 0;
			break;
	}
	return 0;
}

// You must implement this function.
// It is called when the device receives a Device Write packet.
// Updates param to new value passed in data.
//    param   -   Parameter index
//    data    -   value to write, in little-endian bytes
//    len     -   number of bytes in data ** Not included in lowcar refactor
//
//   return  -   size of bytes written on success; otherwise return 0
uint32_t PolarBear::device_write (uint8_t param, uint8_t *data_buf)
{
  switch (param) {

		case DUTY_CYCLE:
			this.driveMode = MANUALDRIVE;
			this.pwmInput = ((float *)data)[0];
			return sizeof(float);
			break;

		case PID_POS_SETPOINT:
			this.driveMode = PID_POS;
			this.pid.setSetpoint(((double *)data)[0]);
			return sizeof(double);
			break;

		case PID_POS_KP:
			this.pid.setCoefficients(((double *)data)[0], this.pid.getKI(), this.pid.getKD());
			return sizeof(double);
			break;

		case PID_POS_KI:
			this.pid.setCoefficients(this.pid.getKP(), ((double *)data)[0], this.pid.getKD());
			return sizeof(double);
			break;

		case PID_POS_KD:
			this.pid.setCoefficients(this.pid.getKP(), this.pid.getKI(), ((double *)data)[0]);
			return sizeof(double);
			break;

		case CURRENT_THRESH:
			setCurrentThreshold(((float *)data)[0]);
			return sizeof(float);
			break;

		case ENC_POS:
			if ((float) data[0] == 0) {
				resetEncoder();
				return sizeof(float);
			}
			break;

		case ENC_VEL:
			break;

		case MOTOR_CURRENT:
			break;

		case DEADBAND:
			this.deadBand = ((float *)data)[0];
			return sizeof(float);
			break;

		case MOTOR_ENABLED: // Lowcar: Use device_enable instead to turn on the device
			break;

		case PWM_INPUT: // Lowcar: replaces resetPWMInput
			this.pwmInput = 0
			return sizeof(float);
			break;

		case DRIVE_MODE: // Lowcar: replaces resetDriveMode
			this.driveMode = MANUALDRIVE
			return sizeof(uint8_t);
			break;

		default:
			return 0;
	}
	return 0;
}

void PolarBear::device_enable ()
{
  encoderSetup();
  setup_LEDs();
  test_LEDs();
  driveMode = MANUALDRIVE;

	// From old motor.cpp motorSetup()
	pinMode(feedback,INPUT);
	pinMode(PWM1, OUTPUT);
	pinMode(PWM2, OUTPUT);

	motorEnabled = true;
}

// It is called when the BBB sends a message to the Smart Device tellinng the Smart Device to disable itself.
// Consult README.md, section 6, to see what exact functionality is expected out of disable.
void PolarBear::device_disable ()
{
	this.pid.setCoefficients(1, 0, 0);
	resetEncoder();
	this.device_write(PWM_INPUT, 0);
	this.device_write(DRIVE_MODE, 0);
	this.motorEnabled = false;
}

void PolarBear::device_actions ()
{
	ctrl_LEDs();
	pid.setSetpoint(pwmInput);
	drive(pid.compute());
}

/* Given a value between -1 and 1 inclusive,
** analogWrite to the appropriate pins to accelerate/decelerate
** Negative indicates moving backwards; Positive indicates moving forwards.
** If moving forwards, set pwm1 to 255 (stop), then move pwm2 down
** If moving backwards, set pwm2 to 255, then move pwm1 down
** Make sure that at least one of the pins is set to 255 at all times.
*/
void drive(float target)
{
	int goal = abs((int) (target * 255));
	int direction = (target > 0) ? 1 : ((target < 0) ? -1 : 0);
	int pwm_difference;
	int delay = 1 / this.dpwm_dt; // About 784
	if (direction > 0) { // Moving forwards
		for (; currpwm1 < 255; currpwm1++) { // Set pwm1 to 255
			analogWrite(PWM1, currpwm1);
			delayMicroseconds(delay);
		}
		pwm_difference = currpwm2 - goal;
		if (pwm_difference < 0) { // Increase pwm2 (Move forward slower)
			for (; currpwm2 < goal; currpwm2++) {
				analogWrite(PWM2, currpwm2);
				delayMicroseconds(delay);
			}
		} else { // Decrease pwm2 (Move forward faster)
			for (; currpwm2 > goal; currpwm2--) {
				analogWrite(PWM2, currpwm2);
				delayMicroseconds(delay);
			}
		}
	} else if (direction < 0) { // Moving backwards
		for (; currpwm2 < 255; currpwm2++) { // Set pwm2 to 255
			analogWrite(PWM2, currpwm2);
			delayMicroseconds(delay);
		}
		pwm_difference = currpwm1 - goal;
		if (pwm_difference < 0) { // Increase pwm1 (Move backwards slower)
			for (; currpwm1 < goal; currpwm1++) {
				analogWrite(PWM1, currpwm1);
				delayMicroseconds(delay);
			}
		} else { // Decrease pwm1 (Move backwards faster)
			for (; currpwm1 > goal; currpwm1--) {
				analogWrite(PWM1, currpwm1);
				delayMicroseconds(delay);
			}
		}
	} else { // Stopping; must set both to 255
		for (; currpwm1 < 255; currpwm1++) {
			analogWrite(PWM1, currpwm1);
			delayMicroseconds(delay);
		}
		for (; currpwm2 < 255; currpwm2++) {
			analogWrite(PWM2, currpwm2);
			delayMicroseconds(delay);
		}
		return;
	}
}
