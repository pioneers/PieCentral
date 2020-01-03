 #include "PolarBear.h"
//#include "motor.h" // Merged
#include "pid.h"
#include "encoder.h"
//#include "current_limit.h"
#include "LED.h"
#include "pindefs.h"

//#include <avr/wdt.h>

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
	POLAR_BEAR,     // Device Type
	0x01,           // Year
	UID_RANDOM,     // ID
};
///////////////////////////////////////////////

/** Variables moved to device constructor
//A space for constants.
float pwmInput = 0; //Value that is received from hibike and is the goal PWM
uint8_t driveMode = 0;

//From old motor.cpp
bool motorEnabled = false;
float deadBand = 0.05;
//bool invHigh = false; Deprecated for lowcar
int currpwm1 = 0;
int currpwm2 = 0;
int delayMod = 1;
float dpwm_dt = 255 / 200000; */

// Lowcar: constructor
PolarBear::PolarBear () : Device (DeviceID::POLAR_BEAR, 2),  encdr(encoder0PinA, encoder0PinB), msngr(), pid(0, 0, 0, 0, millis(), encdr) // Double check
{
	this->pwmInput = 0; // Setpoint
	this->driveMode = 0;
	this->motorEnabled = false;
	this->deadBand = 0.05;
	this->currpwm1 = 255;
	this->currpwm2 = 255;
	this->delayMod = 1;
	this->dpwm_dt = 255 / 200000;
}

/** Main loop function; moved to device_actions
void PolarBear::loop()
{
  ctrl_LEDs();
	// hibike_loop();
	ctrl_pwm(); //actually drive the motor (function in current_limit.cpp)
	//wdt_reset();
} */

// You must implement this function.
// It is called when the device receives a Device Data Update packet.
// Modifies data_buf to contain the parameter value.
//    param           -   Parameter index
//    data_buf -   buffer to return data in, little-endian
//    buf_len         -   Maximum length of the buffer
//
//    return          -   sizeof(value) on success; 0 otherwise
uint8_t PolarBear::device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len)
{
  float* float_buf;

	switch (param) {

		case DUTY_CYCLE:
			if(buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			//float_buf[0] = readPWMInput();
			device_read(PWM_INPUT, float_buf[0], 32); // Replaces above; double check
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
/**
		case PID_VEL_SETPOINT:
			break;

		case PID_VEL_KP:
			break;

		case PID_VEL_KI:
			break;

		case PID_VEL_KD:
			break;
*/
		case CURRENT_THRESH:
			break;

		case ENC_POS:
			if (buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = encdr->readPos();
			return sizeof(float);
			break;

		case ENC_VEL:
			if (buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = encdr->readVel();
			return sizeof(float);
			break;

		case MOTOR_CURRENT:
			if (buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = (analogRead(feedback) / 0.0024); //Used to call readCurrent() feedback is in pindefs.h
			return sizeof(float);
			break;

		case DEADBAND:
			if (buf_len< sizeof(float)){
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->deadBand; //Used to call readDeadBand in motor.cpp
			return sizeof(float);
			break;

		case MOTOR_ENABLED: // Lowcar: Reads whether or not motor is enabled.
			if (buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->motorEnabled; // Double check
			return sizeof(float);
			break;

		case PWM_INPUT: // Lowcar: Replacement for readPWMInput
			if (buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->pwmInput;
			return sizeof(float);
			break;

		case DRIVE_MODE: // Lowcar: Replacement for readDriveMode
			if (buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->driveMode;
			return sizeof(float);
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
			//motorEnable(); // Was merged into device_enable ...
			//disablePID(); Not sure if this is still needed
			this->driveMode = MANUALDRIVE;
			this->pwmInput = ((float *)data)[0];
			return sizeof(float);
			break;

		case PID_POS_SETPOINT:
			//motorEnable(); // Was merged into device_enable ...
			this->driveMode = PID_POS;
			//enablePos(); Not needed
			//setPosSetpoint(((float *)data)[0]); See below
			this->pid.setSetpoint(((double *)data)[0]);
			return sizeof(float);
			break;

		case PID_POS_KP:
			//setPosKP(((float *)data)[0]);
			this->pid.setCoefficients(((double *)data)[0], this->pid.getKI(), this->pid.getKD());
			return sizeof(float);
			break;

		case PID_POS_KI:
			//setPosKI(((float *)data)[0]);
			this->pid.setCoefficients(this->pid.getKP(), ((double *)data)[0], this->pid.getKD());
			return sizeof(float);
			break;

		case PID_POS_KD:
			//setPosKD(((float *)data)[0]);
			this->pid.setCoefficients(this->pid.getKP(), this->pid.getKI(), ((double *)data)[0]);
			return sizeof(float);
			break;
/**
		case PID_VEL_SETPOINT:
			motorEnable(); // Was merged into device_enable ...
			driveMode = PID_VEL;
			enableVel();
			setVelSetpoint(((float *)data)[0]);
			return sizeof(float);
			break;

		case PID_VEL_KP:
			setVelKP(((float *)data)[0]);
			return sizeof(float);
			break;

		case PID_VEL_KI:
			setVelKI(((float *)data)[0]);
			return sizeof(float);
			break;

		case PID_VEL_KD:
			setVelKD(((float *)data)[0]);
			return sizeof(float);
			break;
*/
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
			this->deadBand = ((float *)data)[0]; // used to call setDeadBand in motor
			return sizeof(float);
			break;

		case MOTOR_ENABLED: // Lowcar: Use device_enable instead to turn on the device
			break;

		case PWM_INPUT: // Lowcar: replaces resetPWMInput
			this->pwmInput = 0
			break;

		case DRIVE_MODE:
			this->driveMode = MANUALDRIVE
			break;

		default:
			return 0;
	}
	return 0;
}

// Enable me
void PolarBear::device_enable ()
{
  //motorSetup(); // See below
  //currentLimitSetup();
  encoderSetup();
  //PIDSetup(); Not sure if this is needed
  setup_LEDs();
  test_LEDs();
  //hibike_setup(); //use default heartbeat rates. look at /lib/hibike/hibike_device.cpp for exact values
  //motorDisable(); // motor.device_disable (Vincent: Probably remove this)
  driveMode = MANUALDRIVE;
  // Enable the watchdog timer, with a one second period
  //wdt_reset();
  //wdt_enable(WDTO_1S);


	// From old motor.cpp motorSetup()
	pinMode(feedback,INPUT);
	pinMode(PWM1, OUTPUT);
	pinMode(PWM2, OUTPUT);
	//pinMode(INV, OUTPUT); INV pin deprecated
	//digitalWrite(INV, LOW); INV pin deprecated

	// From old motor.cpp motorEnable()
	//clearFault();
	motorEnabled = true;

}

// Disable me
// It is called when the BBB sends a message to the Smart Device tellinng the Smart Device to disable itself.
// Consult README.md, section 6, to see what exact functionality is expected out of disable.
void PolarBear::device_disable ()
{
	//Used to just call motor.device_disable();
	//Body from motor.device_disable() below
	//disablePID(); Dont think this is needed
	//resetPID(); See below
	this->pid.setCoefficients(1, 0, 0);
	resetEncoder();
	//resetPWMInput(); See below
	this.device_write(PWM_INPUT, 0);
	//resetDriveMode(); See below
	this.device_write(DRIVE_MODE, 0);
	this->motorEnabled = false;
}


void PolarBear::device_actions ()
{
	ctrl_LEDs();
	// hibike_loop();
	//ctrl_pwm(); //actually drive the motor (function in current_limit.cpp)
	//wdt_reset();
	//TODO: Get value from PID and call drive()
	pid.setSetpoint(pwmInput);
	drive(pid.compute());
}


/* Replaced by device_read, device_write
float readPWMInput()
{
	return pwmInput;
}

void resetPWMInput()
{
	pwmInput = 0;
}

uint8_t readDriveMode()
{
	return driveMode;
}

void resetDriveMode()
{
	driveMode = MANUALDRIVE;
}
*/


// **************************
// Methods from old Motor.cpp
// **************************

/* Deprecated for lowcar
// Refactor to run linearly
// pwm2 is forward
// pwm1 is backward
// one always at 255
void change_pwm2(int current, int target, bool flip) {
	int pwm_difference;
        if (!flip) {
		pwm_difference = current - target;
		if (pwm_difference < 0) {
			pwm_difference *= -1;
		}
	} else {
		pwm_difference = (255 - current) + (255 - target);
	}
	float total_time = pwm_difference / dpwm_dt;
	int unit_delay = (int) (total_time / pwm_difference);
	if (!flip) {
		if (target > current) {
			for (; current < target; current++) {
				analogWrite(PWM2, current);
				delayMicroseconds(unit_delay);
			}
		} else {
			for (; current > target; current--) {
				analogWrite(PWM2, current);
				delayMicroseconds(unit_delay);
			}
		}
	} else {
		for (; current < 255; current++) {
			analogWrite(PWM2, current);
			delayMicroseconds(unit_delay);
		}
		if (invHigh) {
			digitalWrite(INV, LOW);
			invHigh = false;
		} else {
			digitalWrite(INV, HIGH);
			invHigh = true;
		}
		for (; current > target; current--) {
			analogWrite(PWM2, current);
			delayMicroseconds(unit_delay);
		}
	}
	currpwm2 = target;
}

//takes a value from -1 to 1 inclusive and writes to the motor and sets the PWM1 and PWM2 pins for direction
void drive(float target)
{
	if (target < -deadBand) {
		int goal = 255 + (int) (target * 255);
		change_pwm2(currpwm2, goal, !invHigh);
	} else if (target > deadBand) {
		target = target * -1;
		int goal = 255 + (int) (target * 255);
		change_pwm2(currpwm2, goal, invHigh);
	} else {
		change_pwm2(currpwm2, 255, false);
	}
} */


// New lowcar drive
// Target is a value from -1 to 1 inclusive
// pwm2 is forward
// pwm1 is backward
// one always at 255
void drive(float target)
{
	int goal = (int) (target * 255);
	int direction = (target > 0) ? 1 : ((target < 0) ? -1 : 0);
	int pwm_difference;
	if (direction > 0) {
		for (; currpwm1 < 255; currpwm1++) { // Set pwm1 to 0
			analogWrite(PWM1, currpwm1);
			//delay
		}
		pwm_difference = currpwm2 - goal;
		if (pwm_difference < 0) { // Increase pwm2
			for (; currpwm2 < goal; currpwm2++) {
				analogWrite(PWM2, currpwm2);
				//delay
			}
		} else {
			for (; currpwm2 > goal; currpwm2--) {
				analogWrite(PWM2, currpwm2);
				//delay
			}
		}
	} else if (direction < 0) { // Going backwards must set pwm2 to 255
		for (; currpwm2 < 255; currpwm2++) {
			analogWrite(PWM2, currpwm2);
			//delay
		}
		pwm_difference = currpwm1 - goal;
		if (pwm_difference < 0) {
			for (; currpwm1 < goal; currpwm1++) {
				analogWrite(PWM1, currpwm1);
				//delay
			}
		} else {
			for (; currpwm1 > goal; currpwm1--) {
				analogWrite(PWM1, currpwm1);
				//delay
			}
		}
	} else { // Stopping must set both to 255
		for (; currpwm1 < 255; currpwm1++) {
			analogWrite(PWM1, currpwm1);
			//delay
		}
		for (; currpwm2 < 255; currpwm2++) {
			analogWrite(PWM2, currpwm2);
			//delay
		}
		return;
	}
}

/* Deprecated from current limit
void clearFault()
{
	analogWrite(PWM1, 255);
	analogWrite(PWM2, 255);
	currpwm2 = 255;
}
*/
