#ifndef PINDEFS_H
#define PINDEFS_H


//Pins.  A0 is proper arduino syntax

//leaving this here for reference
// #define PWM 			9
// #define enable_pin 		21
// #define enableAnalog 	A3
// #define current_pin 	8
// #define INA 			16
// #define INB 			10

#define PWM1 			6 //now used to drive the thingy, used to be INA and INB
#define PWM2			9
#define feedback 		A3		 //indicator for safety, possible new current_pin?
#define LED_RED 		2 //leds are just pin changes
#define LED_YELLOW 		3
#define LED_GREEN 		4
#define encoder0PinA  	14 //encoders are the same fucntionality
#define encoder0PinB  	15
#define INV				5 //digitalwrite to low or else things will go backwards

#endif /* PINDEFS_H */
