#ifndef SAFETY_H
#define SAFETY_H
extern bool unsafe_status;

#include "eeprom.h"
#include "battery_buzzer.h"
#include "pitches.h"

void handle_safety();
bool is_unsafe();
void buzz(boolean should_buzz);


#endif