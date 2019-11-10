#include "StatusLED.h"

StatusLED::StatusLED ()
{
	pinMode(LED_PIN, OUTPUT);
	digitalWrite(LED_PIN, LOW);
	led_enabled = false;
}

StatusLED::toggle ()
{
	(led_enabled) ? digitalWrite(LED_PIN, LOW) : digitalWrite(LED_PIN, HIGH);
	led_enabled = !led_enabled;
}