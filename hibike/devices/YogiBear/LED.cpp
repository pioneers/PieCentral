#include "LED.h"
#include "pindefs.h"
#include "encoder.h"
#include "current_limit.h"
#include "motor.h"
#include "Arduino.h"

bool redOn = false;
bool yellowOn = false;
bool greenOn = false;

//place all LED control functions in here
void ctrl_LEDs() {
	//control red LED state
	if(readVel() < 0) {
		redOn = true;
	} else {
		redOn = false;
	}

	//control yellow LED state
	if(read_limit_state() == 2 || read_limit_state() == 3) { //limit state number
		yellowOn = true;
	} else {
		yellowOn = false;
	}

	//control green LED state
	if(readVel() > 0) {
		greenOn = true;
	} else {
		greenOn = false;
	}

	//All LEDs on when disabled
	if(!isMotorEnabled()) {
		redOn = true;
		yellowOn = true;
		greenOn = true;
	}

	if(redOn) {
		digitalWrite(LED_RED, HIGH);
	} else {
		digitalWrite(LED_RED, LOW);
	}

	if(yellowOn) {
		digitalWrite(LED_YELLOW, HIGH);
	} else {
		digitalWrite(LED_YELLOW, LOW);
	}

	if(yellowOn) {
		digitalWrite(LED_GREEN, HIGH);
	} else {
		digitalWrite(LED_GREEN, LOW);
	}

}

void test_LEDs()
{
	digitalWrite(LED_GREEN,HIGH);
	digitalWrite(LED_RED,HIGH);
	digitalWrite(LED_YELLOW,HIGH);

	delay(1000);

	digitalWrite(LED_GREEN,LOW);
	digitalWrite(LED_RED,LOW);
	digitalWrite(LED_YELLOW,LOW);
}

void setup_LEDs()
{
	pinMode(LED_GREEN, OUTPUT);
	pinMode(LED_RED, OUTPUT);
	pinMode(LED_YELLOW, OUTPUT);
}
