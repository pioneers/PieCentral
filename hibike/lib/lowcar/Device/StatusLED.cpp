#include "StatusLED.h"

StatusLED::StatusLED ()
{
	pinMode(StatusLED::LED_PIN, OUTPUT);
	digitalWrite(StatusLED::LED_PIN, LOW);
	led_enabled = false;
}

void StatusLED::toggle ()
{
	digitalWrite(StatusLED::LED_PIN, led_enabled ? LOW : HIGH);
	led_enabled = !led_enabled;
}
