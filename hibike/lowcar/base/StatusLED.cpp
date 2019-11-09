#include "StatusLED.h"

StatusLED::StatusLED ()
{
	pinMode(LED_PIN, OUTPUT);
	digitalWrite(LED_PIN, lOW);
	led_enabled = false;
}

StatusLED::toggle ()
{
	(led_enabled) ? digitalWrite(LED_PIN, false) : digitalWrite(LED_PIN, true);
	led_enabled = !led_enabled;
}