#define SLEEP		13 //set during setup, should always be high
#define RESET		10 //set during setup, should always be low

#define AIN1		5 //first motor, PWM1 
#define AIN2		9 //first motor, PWM2
#define BIN1		6 //second motor, PWM1
#define BIN2		3 //second motor, PWM2

#define LED_RED		A3	//red
#define LED_YELLOW	A4	//yellow
#define LED_GREEN	A5	//green

#define HEARTBEAT	A2	//flashes on heartbeats

#define SCS		11	//opens communication to motor controller chip during setup

#define AENC1		1	//motor 1, first encoder pin, this is the interrupt pin
#define AENC2		A0	//motor 1, second encoder pin

#define BENC1		2	//motor 2, first encoder pin, this is the interrupt pin
#define BENC2		0	//motor 2, second encoder pin (can also be an interrupt pin)
