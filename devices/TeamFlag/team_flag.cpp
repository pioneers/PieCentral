#include "team_flag.h"


int params[NUM_PARAMS] = {0};


const uint8_t pins[NUM_PINS] = {BLUE, YELLOW, STAT0, STAT1, STAT2, STAT3};
uint64_t modePrevTime, modePeriod=1000;
uint32_t temp;
uint8_t temp8;

void setup() {
  hibike_setup();
  // Setup sensor input
  for (int i = 0; i < NUM_PINS; i++) {
    digitalWrite(pins[i], LOW);
    pinMode(pins[i], OUTPUT);
  }

  // Inital param values
  params[0] = TEAM_NONE;
  params[1] = MODE_INITIAL;
  for (int i=2; i<NUM_PARAMS; i++) {
    params[i] = 0;
  }
  setupMode(params[1]);
  modePrevTime = millis();
}


void loop() {
  hibike_loop();
  modeUpdateLeds(params[1]);
}

uint8_t data_update(uint8_t* data_update_buf, size_t buf_len) {
  uint8_t offset = 0;
  return offset;
}
uint32_t device_status(uint8_t param) {
  return params[param];
}

uint32_t device_update(uint8_t param, uint32_t value) {
  /*enum {
    MODE_INITIAL = 0,  // Initial mode, switches to direct as soon as any LED is set
    MODE_DIRECT = 1,   // All LEDs controlled by the other parameters
    MODE_DEMO = 2,     // Everything blinking quickly
    MODE_ERROR = 3,    // Blink status LEDs quickly but leave team LEDs
  };*/
  //params[param] = value;
  if (param == 0) {  // Setting the team param overrides the team LEDs (blue and yellow)
    if (value == TEAM_BLUE) {
      digitalWrite(YELLOW, LOW);
      digitalWrite(BLUE, HIGH);
      params[param] = value;
      params[1] = MODE_DIRECT;
      params[2] = 1;
      params[3] = 0;
    }else if (value == TEAM_YELLOW) {
      digitalWrite(BLUE, LOW);
      digitalWrite(YELLOW, HIGH);
      params[param] = value;
      params[1] = MODE_DIRECT;
      params[2] = 0;
      params[3] = 1;
    }
  }else if (param == 1) {  // Set the mode
    if (value == MODE_INITIAL || value == MODE_DEMO || value == MODE_ERROR) {
      params[param] = value;
      setupMode(value);
    }else {
      params[param] = MODE_DIRECT;
    }
  }else {  // Directly set an LED
    uint8_t ledPin = pins[(uint8_t)(param - 2)];
    params[1] = MODE_DIRECT;
    params[param] = setLed(ledPin, (uint16_t)value);
  }

  if (params[1] == MODE_DIRECT) {
    for (int i=0; i<NUM_PINS; i++) {
      setLed(pins[i], (uint16_t)params[i+2]);
    }
  }
  return params[param];
}
uint16_t setLed(uint8_t pin, uint16_t value) {
  if (value == 0) {  // If zero, turn off
    value = 0;
    digitalWrite(pin, LOW);
    pinMode(pin, OUTPUT);
  }else if (!(value & 0x8000)) {  // If positive, just turn on
    value = 1;
    digitalWrite(pin, HIGH);
    pinMode(pin, OUTPUT);
  }else {  // If negative, set the brightness between 0 and 255
    value = -value;
    if (value > 255) {
      value = 255;
    }
    if (pin == BLUE || pin == YELLOW) {  // PWM enabled pins
      analogWrite(pin, value);
    } else {  // Hack half brightness using the input pullup pins
      if (value < 64) {
        digitalWrite(pin, LOW);
        pinMode(pin, OUTPUT);
      }else if (value < 128) {
        pinMode(pin, INPUT);
        digitalWrite(pin, HIGH);
      }else {
        pinMode(pin, OUTPUT);
        digitalWrite(pin, HIGH);
      }
    }
    return -value;
  }
  return value;
}
void setupMode(uint8_t mode) {
  modePrevTime = millis();
  switch (mode) {
    case MODE_INITIAL:
      modePeriod = 4000;
      for (int i=0; i<2; i++) {
        digitalWrite(pins[i], LOW);
        pinMode(pins[i], OUTPUT);
      }
      for (int i=2; i<NUM_PINS; i++) {
        pinMode(pins[i], INPUT);
        digitalWrite(pins[i], HIGH);
      }
      return;
    case MODE_DEMO:
      modePeriod = 1000;
      for (int i=0; i<NUM_PINS; i++) {
        digitalWrite(pins[i], LOW);
        pinMode(pins[i], OUTPUT);
      }
      return;
    case MODE_ERROR:
      modePeriod = 250;
      for (int i=0; i<2; i++) {
        setLed(pins[i], (uint16_t)params[i+2]);
      }
      for (int i=2; i<NUM_PINS; i++) {
        pinMode(pins[i], OUTPUT);
        digitalWrite(pins[i], HIGH);
      }
      return;
    default: return;
  }
}
void modeUpdateLeds(uint8_t mode) {
  uint64_t currTime = millis();
  if (currTime - modePrevTime >= modePeriod) {
    modePrevTime += modePeriod;
  }
  temp = (uint32_t)(currTime - modePrevTime);
  switch (mode) {
    case MODE_DIRECT: return;
    case MODE_INITIAL:
      temp8 = (uint8_t)(8*(pow(32, (temp >= 2000 ? (3999-temp) : temp)/2000.0)-1));
      for (int i=0; i<2; i++) {
        analogWrite(pins[i], temp8);
      }
      return;
    case MODE_DEMO:
      digitalWrite(BLUE, ((temp/500)&1));
      digitalWrite(YELLOW, (((temp+250)/500)&1));
      digitalWrite(STAT0, (((temp+125*0)/500)&1));
      digitalWrite(STAT1, (((temp+125*1)/500)&1));
      digitalWrite(STAT2, (((temp+125*2)/500)&1));
      digitalWrite(STAT3, (((temp+125*3)/500)&1));
      return;
    case MODE_ERROR:
      temp8 = temp >= 125 ? LOW : HIGH;
      for (int i=2; i<NUM_PINS; i++) {
        digitalWrite(pins[i], temp8);
      }
      return;
  }
}