#include "KoalaBear.h"

//********************************* constants and variables used for setting up the controller ********************//
//ask electrical for what they mean
#define CTRL_REG      0b000
#define TORQUE_REG    0b001

//Control Register options
//Dead time
#define DTIME_410_ns  0b00
#define DTIME_460_ns  0b01
#define DTIME_670_ns  0b10
#define DTIME_880_ns  0b11

//Current sense gain
#define ISGAIN_5      0b00
#define ISGAIN_10     0b01
#define ISGAIN_20     0b10
#define ISGAIN_40     0b11

//Enable or disable motors
#define ENABLE        0b1
#define DISABLE       0b0

//Set VREF scaling out of 256
#define TORQUE        0x70

uint16_t ctrl_read_data;
uint16_t torque_read_data;

//*********************************************** labels for useful indices **********************************//
typedef enum {
	//params for the first motor
	DUTY_CYCLE_A = 0,		//desired speed for students, between -1 and 1 inclusive
	PID_KP_A = 8,			//these three are the PID coefficients
	PID_KI_A = 2,
	PID_KD_A = 3,
	ENC_A = 4,				//encoder position, in ticks
	DEADBAND_A = 5,			//between 0 and 1, magnitude of duty cycle input under which the motor will not move
	MOTOR_ENABLED_A = 6,	//true or false, depending on whether it's enabled
	DRIVE_MODE_A = 7, 		//either manula or pid drive mode

	//params repeated for the second motor
	DUTY_CYCLE_B = 1,
	PID_KP_B = 9,
	PID_KI_B = 10,
	PID_KD_B = 11,
	ENC_B = 12,
	DEADBAND_B = 13,
	MOTOR_ENABLED_B = 14,
	DRIVE_MODE_B = 15,
} param;

typedef enum {
	MANUAL = 0,			//no control
	PID = 1				//PID control
} DriveModes;

typedef enum {
	MTRA = 1,
	MTRB = 0,
} mtrs;

//********************************************************* MAIN KOALABEAR CODE ***********************************//

KoalaBear::KoalaBear () : Device (DeviceID::KOALA_BEAR, 13), //,  encdr(encoder0PinA, encoder0PinB), pid(0.0, 0.0, 0.0, 0.0, (double) millis(), encdr)
	desired_speeds(), drivemodes(), enabled(), deadbands(), led()
{
	//this->pid = new PID(0.0, 1.0, 0.0, 0.0, (double) millis()); //PID(double SetPoint, double KP, double KI, double KD, double initTime)
	this->desired_speeds = (float *) calloc(2, sizeof(float));
	this->drivemodes = (uint8_t *) calloc(2, sizeof(uint8_t));
	this->enabled = (bool *) calloc(2, sizeof(bool));
	this->deadbands = (float *) calloc(2, sizeof(float));

	this->deadbands[MTRA] = 0.05;
	this->deadbands[MTRB] = 0.05;

	this->prev_led_time = millis();
	this->curr_led_mtr = MTRA;
}

/* This function is called when the device receives a Device Read packet.
 * It modifies DATA_BUF to contain the most recent value of parameter PARAM.
 * param			-   Parameter index (0, 1, 2, 3 ...)
 * data_buf 		-   Buffer to return data in, little-endian
 * buf_len			-   Number of bytes available in data_buf to store data
 *
 * return			-   sizeof(<parameter_value>) on success; 0 otherwise
 */
uint8_t KoalaBear::device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len)
{
	float *float_buf;
	bool *bool_buf;

	switch (param) {

		case DUTY_CYCLE_A:
			if (data_buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->desired_speeds[MTRA];
			return sizeof(float);
			break;

		//TODO: ask PID controller for motor A for KP
		case PID_KP_A:
			break;

		//TODO: ask PID controller for motor A for KI
		case PID_KI_A:
			break;

		//TODO: ask PID controller for motor A for KD
		case PID_KD_A:
			break;

		case ENC_A:
		/*
			if (data_buf_len < sizeof(double)) {
				return 0;
			}
			double_buf = (double *) data_buf;
			double_buf[0] = this->pid->readPos();
			return sizeof(double);
		*/
			break;

		case DEADBAND_A:
			if (data_buf_len < sizeof(float)){
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->deadbands[MTRA];
			return sizeof(float);
			break;

		case MOTOR_ENABLED_A:
			if (data_buf_len < sizeof(bool)) {
				return 0;
			}
			bool_buf = (bool *) data_buf;
			bool_buf[0] = this->enabled[MTRA];
			return sizeof(bool);
			break;

		case DRIVE_MODE_A:
			if (data_buf_len < sizeof(uint8_t)) {
				return 0;
			}
			data_buf[0] = this->drivemodes[MTRA];
			return sizeof(uint8_t);
			break;

		case DUTY_CYCLE_B:
			if (data_buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->desired_speeds[MTRB];
			return sizeof(float);
			break;

		//TODO: ask PID controller for motor B for KP
		case PID_KP_B:
			break;

		//TODO: ask PID controller for motor B for KI
		case PID_KI_B:
			break;

		//TODO: ask PID controller for motor B for KD
		case PID_KD_B:
			break;

		case ENC_B:
		/*
			if (data_buf_len < sizeof(double)) {
				return 0;
			}
			double_buf = (double *) data_buf;
			double_buf[0] = this->pid->readPos();
			return sizeof(double);
		*/
			break;

		case DEADBAND_B:
			if (data_buf_len < sizeof(float)){
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->deadbands[MTRB];
			return sizeof(float);
			break;

		case MOTOR_ENABLED_B:
			if (data_buf_len < sizeof(bool)) {
				return 0;
			}
			bool_buf = (bool *) data_buf;
			bool_buf[0] = this->enabled[MTRB];
			return sizeof(bool);
			break;

		case DRIVE_MODE_B:
			if (data_buf_len < sizeof(uint8_t)) {
				return 0;
			}
			data_buf[0] = this->drivemodes[MTRB];
			return sizeof(uint8_t);
			break;

		default:
			break;
	}
	return 0;
}

/* This function is called when the device receives a Device Write packet.
 * Updates PARAM to new value contained in DATA.
 * param			-   Parameter index (0, 1, 2, 3 ...)
 * data_buf	 		-   Contains value to write, little-endian
 *
 * return			-   sizeof(<bytes_written>) on success; 0 otherwise
 */
uint32_t KoalaBear::device_write (uint8_t param, uint8_t *data_buf)
{
  switch (param) {

		case DUTY_CYCLE_A:
			this->drivemodes[MTRA] = MANUAL; //remove later once PID added in
			this->desired_speeds[MTRA] = ((float *)data_buf)[0];
			return sizeof(float);
			break;

		case PID_KP_A:
			//this->pid->setCoefficients(((double *)data_buf)[0], this->pid->getKI(), this->pid->getKD());
			return sizeof(double);
			break;

		case PID_KI_A:
			//this->pid->setCoefficients(this->pid->getKP(), ((double *)data_buf)[0], this->pid->getKD());
			return sizeof(double);
			break;

		case PID_KD_A:
			//this->pid->setCoefficients(this->pid->getKP(), this->pid->getKI(), ((double *)data_buf)[0]);
			return sizeof(double);
			break;

		case ENC_A:
		/*
			if ((float) data_buf[0] == 0) {
				this->pid->resetEncoder();
				return sizeof(float);
			}
		*/
			break;

		case DEADBAND_A:
			this->deadbands[MTRA] = ((float *)data_buf)[0];
			return sizeof(float);
			break;

		case MOTOR_ENABLED_A:
			break;

		//TODO: perhaps add functionality to specify which of the two drive modes you should use
		case DRIVE_MODE_A:
			this->drivemodes[MTRA] = MANUAL;
			return sizeof(uint8_t);
			break;

		case DUTY_CYCLE_B:
			this->drivemodes[MTRB] = MANUAL; //remove later for PID functionality
			this->desired_speeds[MTRB] = ((float *)data_buf)[0];
			return sizeof(float);
			break;

		case PID_KP_B:
			//this->pid->setCoefficients(((double *)data_buf)[0], this->pid->getKI(), this->pid->getKD());
			return sizeof(double);
			break;

		case PID_KI_B:
			//this->pid->setCoefficients(this->pid->getKP(), ((double *)data_buf)[0], this->pid->getKD());
			return sizeof(double);
			break;

		case PID_KD_B:
			//this->pid->setCoefficients(this->pid->getKP(), this->pid->getKI(), ((double *)data_buf)[0]);
			return sizeof(double);
			break;

		case ENC_B:
		/*
			if ((float) data_buf[0] == 0) {
				this->pid->resetEncoder();
				return sizeof(float);
			}
		*/
			break;

		case DEADBAND_B:
			this->deadbands[MTRB] = ((float *)data_buf)[0];
			return sizeof(float);
			break;

		case MOTOR_ENABLED_B:
			break;

		case DRIVE_MODE_B:
			this->drivemodes[MTRB] = MANUAL;
			return sizeof(uint8_t);
			break;

		default:
			return 0;
	}
	return 0;
}

/* This function is called in the Device constructor 
 * (or potentially on receiving a Device Enable packet in the future).
 * It should do whatever setup is necessary for the device to operate.
 */
void KoalaBear::device_enable ()
{
	electrical_setup(); //ask electrical about this function (it's hardware setup for the motor controller_
	
    //this->pid->encoderSetup();
    this->led->setup_LEDs();
    this->led->test_LEDs();
    this->drivemodes[MTRA] = MANUAL;
	this->drivemodes[MTRB] = MANUAL; //change to PID once it's implemented

	// From old motor.cpp motorSetup()
	//pinMode(feedback,INPUT);
	pinMode(AIN1, OUTPUT);
	pinMode(AIN2, OUTPUT);
	pinMode(BIN1, OUTPUT);
	pinMode(BIN2, OUTPUT);

	this->enabled[MTRA] = true;
	this->enabled[MTRB] = true;

	this->desired_speeds[MTRA] = 0.0;
	this->desired_speeds[MTRB] = 0.0;
}

/* This function is called when receiving a Device Disable packet, or 
 * when the controller has stopped responding to heartbeat requests.
 digitalWrite(SLEEP, HIGH);
 * It should do whatever cleanup is necessary for the device to disable.
 */
void KoalaBear::device_disable ()
{
	//this->pid->setCoefficients(1, 0, 0);
	//this->pid->resetEncoder();
	
	this->desired_speeds[MTRA] = 0.0;
	this->desired_speeds[MTRB] = 0.0;
	this->drivemodes[MTRA] = MANUAL;
	this->drivemodes[MTRB] = MANUAL;
	this->enabled[MTRA] = false;
	this->enabled[MTRB] = false;
}

/* This function is called each time the device goes through the main loop.
 * Any continuously updating actions the device needs to do should be placed
 * in this function.
 * IMPORTANT: This function should not block!
 */
void KoalaBear::device_actions ()
{
	float target_A, target_B;

	//switch between displaying info about MTRA and MTRB every 2 seconds
	if (millis() - this->prev_led_time > 2000) {
		this->curr_led_mtr = (this->curr_led_mtr == MTRA) ? MTRB : MTRA;
		this->prev_led_time = millis();
	}
	this->led->ctrl_LEDs(this->desired_speeds[this->curr_led_mtr], this->enabled[this->curr_led_mtr]);

	if (this->drivemodes[MTRA] == PID) {
		//this->pid->setSetpoint(this->desired_speeds[MTRA]);
		//target = this->pid->compute();
		target_A = 0.0;
	} else {
		target_A = this->desired_speeds[MTRA];
	}
	
	if (this->drivemodes[MTRB] == PID) {
		//this->pid->setSetpoint(this->desired_speeds[MTRB]);
		//target = this->pid->compute();
		target_B = 0.0;
	} else {
		target_B = this->desired_speeds[MTRB];
	}
	
	digitalWrite(SLEEP, HIGH);
	digitalWrite(RESET, LOW);

	//send target duty cycle to drive function
	drive(target_A, MTRA);
	drive(target_B *-1.0, MTRB); //MTRB by default moves in the opposite direction as motor A
}

//******************************************** KOALABEAR HELPER FUNCTIONS *************************//
//used for setup; ask electrical for how it works / what it does
void KoalaBear::write_current_lim() 
{
	SPI.beginTransaction(SPISettings(100000, MSBFIRST, SPI_MODE0));
	digitalWrite(SCS, HIGH);
	SPI.transfer16((0 << 15) + (CTRL_REG << 12) + (DTIME_410_ns << 10) + (ISGAIN_20 << 8) + ENABLE);
	SPI.endTransaction();
	digitalWrite(SCS, LOW);
	SPI.beginTransaction(SPISettings(100000, MSBFIRST, SPI_MODE0));
	digitalWrite(SCS, HIGH);
	SPI.transfer16((0 << 15) + (TORQUE_REG << 12) + TORQUE);
	SPI.endTransaction();
	digitalWrite(SCS, LOW);
}

//used for setup; ask electrical for how it works / what it does
void KoalaBear::read_current_lim() 
{
	SPI.beginTransaction(SPISettings(100000, MSBFIRST, SPI_MODE0));
	digitalWrite(SCS, HIGH);
	ctrl_read_data = (uint16_t) SPI.transfer16((1 << 15) + (CTRL_REG << 12));
	SPI.endTransaction();
	digitalWrite(SCS, LOW);
	SPI.beginTransaction(SPISettings(100000, MSBFIRST, SPI_MODE0));
	digitalWrite(SCS, HIGH);
	torque_read_data = (uint16_t) SPI.transfer16((1 << 15) + (TORQUE_REG << 12));
	SPI.endTransaction();
	digitalWrite(SCS, LOW);
}

//used for setup; ask electrical for how it works / what it does
void KoalaBear::electrical_setup()
{
	SPI.begin();
	
	pinMode(HEARTBEAT, OUTPUT);
	pinMode(RESET, OUTPUT);
	pinMode(SLEEP, OUTPUT);
	pinMode(SCS, OUTPUT);

	delay(100);

	digitalWrite(SLEEP, HIGH);
	digitalWrite(RESET, LOW);
	
	digitalWrite(HEARTBEAT, HIGH);
	digitalWrite(SCS, LOW);
	
	write_current_lim();
	read_current_lim();
}

/* Calculates the sign of a float. */
int KoalaBear::sign (float x) {
    if (x > 0) {
        return 1;
    } else if (x < 0) {
        return -1;
    }
    return 0;
}

/* Given a TARGET between -1 and 1 inclusive, and a motor MTR,
** analogWrite to the appropriate pins to accelerate/decelerate
** Negative indicates moving backwards; Positive indicates moving forwards.
** If moving forwards, set pwm2 to 255 (stop), then move pwm1 down
** If moving backwards, set pwm1 to 255, then move pwm2 down
** Make sure that at least one of the pins is set to 255 at all times.
*/
void KoalaBear::drive (float target, uint8_t mtr)
{
	int pin1 = (mtr == MTRA) ? AIN1 : BIN1; //select the correct pins based on the motor
	int pin2 = (mtr == MTRA) ? AIN2 : BIN2;
	
    int direction = sign(target);
	int currpwm1, currpwm2;
    int goal;
	
    if (target == 0) {
        direction = 0;
    } else {
        goal = target * 255 * sign(target); // A number between 0 and 255 inclusive (255 is stop; 0 is max speed);
    }
	int pwm_difference;
	if (direction > 0) { // Moving forwards
		currpwm2 = 255;
		currpwm1 = 255 - goal;
	} else if (direction < 0) { // Moving backwards
		currpwm1 = 255;
		currpwm2 = 255 - goal;
	} else { // Stopping; must set both to 255
		currpwm1 = 255;
		currpwm2 = 255;
	}
	
	analogWrite(pin1, currpwm1);
	analogWrite(pin2, currpwm2);
}
