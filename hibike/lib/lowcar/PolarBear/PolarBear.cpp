#include "PolarBear.h"

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

 typedef enum {
    MANUALDRIVE = 0,
    PID_VEL = 1,
    PID_POS = 2
  } DriveModes;

PolarBear::PolarBear () : Device (DeviceID::POLAR_BEAR, 2) //,  encdr(encoder0PinA, encoder0PinB), pid(0.0, 0.0, 0.0, 0.0, (double) millis(), encdr)
{
	this->pid = new PID(0.0, 1.0, 0.0, 0.0, (double) millis()); //PID(double SetPoint, double KP, double KI, double KD, double initTime)
	this->pwmInput = 0; // Setpoint to be used with PID
	this->driveMode = 0;
	this->motorEnabled = false;
	this->deadBand = 0.05;
	this->currpwm1 = 255;
	this->currpwm2 = 255;
	this->delayMod = 1;
	this->dpwm_dt = 255 / 200000;
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
			if(data_buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->pwmInput; // Same as devie_read on PWMINPUT
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
			if (data_buf_len < sizeof(double)) {
				return 0;
			}
			double_buf = (double *) data_buf;
			double_buf[0] = this->pid->readPos();
			return sizeof(double);
			break;

		case ENC_VEL:
			if (data_buf_len < sizeof(double)) {
				return 0;
			}
			double_buf = (double *) data_buf;
			double_buf[0] = this->pid->readVel();
			return sizeof(double);
			break;

		case MOTOR_CURRENT:
			if (data_buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = (analogRead(feedback) / 0.0024); //feedback def in pindefs.h
			return sizeof(float);
			break;

		case DEADBAND:
			if (data_buf_len< sizeof(float)){
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->deadBand;
			return sizeof(float);
			break;

		case MOTOR_ENABLED: // Lowcar: Reads whether or not motor is enabled.
			if (data_buf_len < sizeof(boolean)) {
				return 0;
			}
			boolean_buf = (boolean *) data_buf;
			boolean_buf[0] = this->motorEnabled;
			return sizeof(boolean);
			break;

		case PWM_INPUT: // Lowcar: Replacement for readPWMInput
			if (data_buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->pwmInput;
			return sizeof(float);
			break;

		case DRIVE_MODE: // Lowcar: Replacement for readDriveMode
			if (data_buf_len < sizeof(uint8_t)) {
				return 0;
			}
			data_buf[0] = this->driveMode;
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
			this->driveMode = MANUALDRIVE;
			this->pwmInput = ((float *)data_buf)[0];
			return sizeof(float);
			break;

		case PID_POS_SETPOINT:
			this->driveMode = PID_POS;
			this->pid->setSetpoint(((double *)data_buf)[0]);
			return sizeof(double);
			break;

		case PID_POS_KP:
			this->pid->setCoefficients(((double *)data_buf)[0], this->pid->getKI(), this->pid->getKD());
			return sizeof(double);
			break;

		case PID_POS_KI:
			this->pid->setCoefficients(this->pid->getKP(), ((double *)data_buf)[0], this->pid->getKD());
			return sizeof(double);
			break;

		case PID_POS_KD:
			this->pid->setCoefficients(this->pid->getKP(), this->pid->getKI(), ((double *)data_buf)[0]);
			return sizeof(double);
			break;

		case CURRENT_THRESH:
			//setCurrentThreshold(((float *)data_buf)[0]);
			//return sizeof(float);
			break;

		case ENC_POS:
			if ((float) data_buf[0] == 0) {
				this->pid->resetEncoder();
				return sizeof(float);
			}
			break;

		case ENC_VEL:
			break;

		case MOTOR_CURRENT:
			break;

		case DEADBAND:
			this->deadBand = ((float *)data_buf)[0];
			return sizeof(float);
			break;

		case MOTOR_ENABLED: // Lowcar: Use device_enable instead to turn on the device
			break;

		case PWM_INPUT: // Lowcar: replaces resetPWMInput
			this->pwmInput = 0;
			return sizeof(float);
			break;

		case DRIVE_MODE: // Lowcar: replaces resetDriveMode
			this->driveMode = MANUALDRIVE;
			return sizeof(uint8_t);
			break;

		default:
			return 0;
	}
	return 0;
}

void PolarBear::device_enable ()
{
    this->pid->encoderSetup();
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
	this->pid->setCoefficients(1, 0, 0);
	this->pid->resetEncoder();
	this->device_write(PWM_INPUT, 0);
	this->device_write(DRIVE_MODE, 0);
	this->motorEnabled = false;
}

void PolarBear::device_actions ()
{
	ctrl_LEDs();
	pid->setSetpoint(pwmInput);
	//drive(pid->compute());
    drive(this->pwmInput); // Temporary change just to test if wheel turns.
}

/* Calculates the sign of a float. */
int PolarBear::sign(float x) {
    if (x > 0) {
        return 1;
    } else if (x < 0) {
        return -1;
    }
    return 0;
}

/* Given a value between -1 and 1 inclusive,
** analogWrite to the appropriate pins to accelerate/decelerate
** Negative indicates moving backwards; Positive indicates moving forwards.
** If moving forwards, set pwm1 to 255 (stop), then move pwm2 down
** If moving backwards, set pwm2 to 255, then move pwm1 down
** Make sure that at least one of the pins is set to 255 at all times.
*/
void PolarBear::drive(float target)
{
    int direction = sign(target);
    int goal;
    if (target == 0) {
        direction = 0;
    } else {
        goal = target * 255 * sign(target); // A number between 0 and 255 inclusive (255 is stop; 0 is max speed);
    }
	int pwm_difference;
	int delay = 1 / this->dpwm_dt; // About 784
	if (direction > 0) { // Moving forwards
		currpwm2 = 255;
		currpwm1 = 255 - goal;

		//for (; currpwm2 < 255; currpwm2++) { // Set pwm2 to 255
		//	analogWrite(PWM2, currpwm2);
		//	delayMicroseconds(delay);
		//}
		//pwm_difference = currpwm1 - goal;
		//for (int step = -sign(pwm_difference); currpwm1 != goal; currpwm1 += step) { // Moves currpwm1 to the goal
		//    analogWrite(PWM1, currpwm1);
		//    delayMicroseconds(delay);
		//}
	} else if (direction < 0) { // Moving backwards
		currpwm1 = 255;
		currpwm2 = 255 - goal;		
		//for (; currpwm1 < 255; currpwm1++) { // Set pwm1 to 255
		//	analogWrite(PWM1, currpwm1);
		//	delayMicroseconds(delay);
		//}
		//pwm_difference = currpwm2 - goal;
		//for (int step = -sign(pwm_difference); currpwm2 != goal; currpwm2 += step) { // Moves currpwm2 to the goal
		//    analogWrite(PWM2, currpwm2);
		//    delayMicroseconds(delay);
		//}
	} else { // Stopping; must set both to 255
		currpwm1 = 255;
		currpwm2 = 255;
		//for (; currpwm1 < 255; currpwm1++) {
		//	analogWrite(PWM1, currpwm1);
		//	delayMicroseconds(delay);
		//}
		//for (; currpwm2 < 255; currpwm2++) {
		//	analogWrite(PWM2, currpwm2);
		//	delayMicroseconds(delay);
		//}
		//return;
	}
	analogWrite(PWM1, currpwm1);
	analogWrite(PWM2, currpwm2);
	delayMicroseconds(delay);
}
