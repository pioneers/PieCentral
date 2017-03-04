#include "LED.h"
#include "pindefs.h"
#include "encoder.h"
#include "current_limit.h"
#include "motor.h"
#include "Arduino.h"

//place all LED control functions in here
void ctrl_LEDs() {
	ctrl_RED();
	ctrl_YELLOW();
	ctrl_GREEN();
}

//decides when the red LED is on
void ctrl_RED() {
	if(readVel() < 0) {
		digitalWrite(LED_RED, HIGH);
	} else {
		digitalWrite(LED_RED, LOW);
	}

	if(!isMotorEnabled()) {
		digitalWrite(LED_RED, HIGH);
	}
}

//decides when the yellow LED is on
void ctrl_YELLOW() {
	if(read_limit_state() == 2 || read_limit_state() == 3) { //limit state number
		digitalWrite(LED_YELLOW, HIGH);
	} else {
		digitalWrite(LED_YELLOW, LOW);
	}
	if(!isMotorEnabled()) {
		digitalWrite(LED_YELLOW, HIGH);
	}
}

//decides when the green LED is on
void ctrl_GREEN() {
	if(readVel() > 0) {
		digitalWrite(LED_GREEN, HIGH);
	} else {
		digitalWrite(LED_GREEN, LOW);
	}
	if(!isMotorEnabled()) {
		digitalWrite(LED_GREEN, HIGH);
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
