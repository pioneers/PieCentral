#include "StatusLED.h"

StatusLED::StatusLED ()
{
	pinMode(StatusLED::LED_PIN, OUTPUT);
	digitalWrite(StatusLED::LED_PIN, LOW);
	led_enabled = false;
}

void StatusLED::toggle ()
{
	(led_enabled) ? digitalWrite(StatusLED::LED_PIN, LOW) : digitalWrite(StatusLED::LED_PIN, HIGH);
	led_enabled = !led_enabled;
}
