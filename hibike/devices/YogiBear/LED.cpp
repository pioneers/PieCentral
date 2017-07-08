/* Licensed to Pioneers in Engineering under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Pioneers in Engineering licenses
 * this file to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 *  with the License.  You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 */ under the License
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
	bool redOn = false;

	if(readVel() < 0 || !isMotorEnabled()) {
		redOn = true;
	}

	if(redOn) {
		digitalWrite(LED_RED, HIGH);
	} else {
		digitalWrite(LED_RED, LOW);
	}
}

//decides when the yellow LED is on
void ctrl_YELLOW() {
	bool yellowOn = false;

	if(read_limit_state() == 2 || read_limit_state() == 3 || !isMotorEnabled()) { //limit state number
		yellowOn = true;
	}

	if(yellowOn) {
		digitalWrite(LED_YELLOW, HIGH);
	} else {
		digitalWrite(LED_YELLOW, LOW);
	}
}

//decides when the green LED is on
void ctrl_GREEN() {
	bool greenOn = false;

	if(readVel() > 0 || !isMotorEnabled()) {
		greenOn = true;
	} 

	if(greenOn) {
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
