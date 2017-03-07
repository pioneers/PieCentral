#include "EEPROM.h"
#include "battery_buzzer.h"

uint8_t safe, connected;

// Variables used in the ADC read timer interrupt
const uint8_t cellPins[NUM_CELLS] = BATT_INPUT;
const uint8_t channelNums[NUM_CELLS] = BATT_CHANNELS;  // The ADC channels for A0, A1, A2 on atmega32u4
uint16_t analogAccumArrs[2][NUM_CELLS] = {{0, 0, 0}, {0, 0, 0}};
float cellVoltageArrs[2][NUM_CELLS] = {{0, 0, 0}, {0, 0, 0}};
float cellTotalArr[2] = {0, 0};
uint8_t disconnectedArr[2] = {0, 0};
volatile uint8_t latestAnalogAccum = 0;  // 0 or 1 index into analogAccumArrs, 0xFF means no data yet
volatile uint8_t lastInputIndex = 0;
volatile uint8_t inputIndex = 0;
volatile uint8_t inputSample = 0;
volatile uint32_t lastUpdateTime = 0;
volatile float cellScale[NUM_CELLS] = DEFAULT_CALIBRATION;
int measureCounter = 0;
uint32_t lastMeasureTime = 0;

// unbalanced for each cell is relative to the cell after it mod 3
cell_state cell_states[NUM_CELLS] = {CELL_SAFE, CELL_SAFE, CELL_SAFE};

// normal arduino setup function, you must call hibike_setup() here
void setup() {
  for (int i=0; i<NUM_CELLS; i++) {
    pinMode(cellPins[i], INPUT);
  }
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(BUZZER_LED_PIN, OUTPUT);
  pinMode(READ_ENABLE_PIN, OUTPUT);
  digitalWrite(READ_ENABLE_PIN, HIGH);
  digitalWrite(BUZZER_LED_PIN, HIGH);

  calibrationSetup(true);  // Also plays startup tone
  readTimerStart();

  delay(100);  // Wait for the first reading to finish (50ms minimum)

  hibike_setup(500); // Time in milliseconds before timeout on heartbeat
}

// normal arduino loop function, you must call hibike_loop() here
// hibike_loop will look for any packets in the serial buffer and handle them
void loop() {
  cli();
  uint32_t lastTime = lastMeasureTime;
  sei();
  if (millis() - lastTime > MEASURE_DELAY_UNSAFE_MS) {
    // Should never happen
    // Indicates that the timer interrupt stopped working
    tone(BUZZER_PIN, BUZZER_BROKEN_FREQ);
  }
  hibike_loop();
}

uint16_t newAnalogRead(uint8_t channel) {
  // Configure ADC
  ADMUX = (0<<REFS0);  // 1=Set reference voltage to AVcc (5V), 0=External AREF, 3=Internal 2.56V
  ADCSRA = (1<<ADEN) | (7<<ADPS0);  // Enable ADC, set divider to 128 (125kHz when 16MHz clock)

  channel &= 0x07;
  ADMUX = (ADMUX & 0xF8) | channel;  // Select ADC channel

  ADCSRA |= (1<<ADSC);  // Start conversion
  while (ADCSRA & (1<<ADSC));
  return ADC;
}

void calibrationSetup(bool beep) {
  volatile float defaultCellScale[NUM_CELLS] = DEFAULT_CALIBRATION;
  uint8_t arrIndex = latestAnalogAccum;
  memset(analogAccumArrs[arrIndex], 0, NUM_CELLS*sizeof(uint16_t));
  for (int i=0; i<NUM_SAMPLES; i++) {
    for (int j=0; j<NUM_CELLS; j++) {
      analogAccumArrs[arrIndex][j] += newAnalogRead(channelNums[j]);
    }
  }
  bool shouldCalibrate = true;
  for (int j=0; j<NUM_CELLS; j++) {
    cellVoltageArrs[arrIndex][j] = analogAccumArrs[arrIndex][j]*defaultCellScale[j];
    if (cellVoltageArrs[arrIndex][j] < MIN_REF_VOLT || cellVoltageArrs[arrIndex][j] > MAX_REF_VOLT) {
      shouldCalibrate = false;
    }
  }
  cellTotalArr[arrIndex] = cellVoltageArrs[arrIndex][2];
  cellVoltageArrs[arrIndex][2] -= cellVoltageArrs[arrIndex][1];
  cellVoltageArrs[arrIndex][1] -= cellVoltageArrs[arrIndex][0];
  if (shouldCalibrate) {
    // Store calibration to EEPROM
    EEPROM.write(0, 'N');
    for (int j=0; j<NUM_CELLS; j++) {
      cellScale[j] = ((float)REF_VOLT)/analogAccumArrs[arrIndex][j];
      uint8_t *scaleBytes = (uint8_t*)(void*)&cellScale[j];
      for (int k=0; k<4; k++) {
        EEPROM.write(4+j*4+k, scaleBytes[k]);
      }
    }
    EEPROM.write(0, 'C');
    EEPROM.write(1, 'A');
    EEPROM.write(2, 'L');
    EEPROM.write(3, ':');
    if (beep) {
      tone(BUZZER_PIN, NOTE_C3, 0);
      delay(250);
      tone(BUZZER_PIN, NOTE_D3, 0);
      delay(250);
      noTone(BUZZER_PIN);
    }
  } else if(EEPROM.read(0)=='C' && EEPROM.read(1)=='A' && EEPROM.read(2)=='L' && EEPROM.read(3)==':') {
    // Read calibration from EEPROM
    for (int j=0; j<NUM_CELLS; j++) {
      uint8_t *scaleBytes = (uint8_t*)(void*)&cellScale[j];
      for (int k=0; k<4; k++) {
        scaleBytes[k] = EEPROM.read(4+j*4+k);
      }
    }
    if (beep) {
      tone(BUZZER_PIN, NOTE_C4, 0);
      delay(250);
      tone(BUZZER_PIN, NOTE_D4, 0);
      delay(250);
      noTone(BUZZER_PIN);
    }
  } else {
    // Otherwise don't calibrate
    if (beep) {
      tone(BUZZER_PIN, NOTE_C3, 0);
      delay(250);
      tone(BUZZER_PIN, NOTE_B2, 0);
      delay(250);
      noTone(BUZZER_PIN);
    }
  }
}

void readTimerStart() {
  // Configure ADC
  ADMUX = (0<<REFS0);  // 1=Set reference voltage to AVcc (5V), 0=External AREF, 3=Internal 2.56V
  ADCSRA = (1<<ADEN) | (7<<ADPS0);  // Enable ADC, set divider to 128 (125kHz when 16MHz clock)

  // Setup Timer 1 (Timer 0 is for Arduino millis/micro/delay, Timer 3 is for tone)
  // Configure to run at 3125 Hz (every 320 us)
  cli();
  TCCR1A = 0;//(3<<COM3A0);// | (0<<WGM10);  // Reset timer on compare and enable compare A
  TCCR1B = (1<<WGM12) | (5<<CS10);    // Set divider to 1024 (~16kHz for 16MHz clock)
  OCR1A = 4;  // Set period to 5=(4+1) -> 3125Hz
  TCNT1 = 0;  // Reset timer value
  TIFR1 = (1<<OCF1A);  // Clear previous interrupt flag
  TIMSK1 = (1<<OCIE1A);  // Enable interrupt on compare A
  sei();
}

// Run at 3125 Hz (every 320 us)
ISR(TIMER1_COMPA_vect) {
  uint16_t nextVal = ADC;  // Assume that the previous conversion finished
  // Start next analog read
  ADMUX = (ADMUX & 0xF8) | (channelNums[inputIndex] & 0x07);  // Select ADC channel
  ADCSRA |= (1<<ADSC);  // Start conversion
  // Accumulate inputs so an average analog input can be generated
  if(lastInputIndex == inputIndex) {
    // This is the first time
    // there is no data yet
    inputIndex++;
    // Zero the new accumulation array
    memset(analogAccumArrs[!latestAnalogAccum], 0, NUM_CELLS*sizeof(uint16_t));
    disconnectedArr[!latestAnalogAccum] = 0;
  } else {
    analogAccumArrs[!latestAnalogAccum][lastInputIndex] += nextVal;  // Write data to the other output array
    disconnectedArr[!latestAnalogAccum] += nextVal < DISCONNECTED_THRESHOLD;
    if (disconnectedArr[!latestAnalogAccum] > DISCONNECTED_COUNT) {
      disconnectedArr[!latestAnalogAccum] = DISCONNECTED_COUNT;
    }
    if (inputIndex == 0 && inputSample == 0) {
      uint8_t arrIndex = !latestAnalogAccum;
      cellVoltageArrs[arrIndex][0] = analogAccumArrs[arrIndex][0]*cellScale[0];
      cellVoltageArrs[arrIndex][1] = analogAccumArrs[arrIndex][1]*cellScale[1];
      cellTotalArr[arrIndex] = analogAccumArrs[arrIndex][2]*cellScale[2];
      cellVoltageArrs[arrIndex][2] = cellTotalArr[arrIndex] - cellVoltageArrs[arrIndex][1];
      cellVoltageArrs[arrIndex][1] -= cellVoltageArrs[arrIndex][0];
      
      // Just finished taking samples, output the total now
      latestAnalogAccum = !latestAnalogAccum;
      // Zero the new accumulation array
      memset(analogAccumArrs[!latestAnalogAccum], 0, NUM_CELLS*sizeof(uint16_t));
      disconnectedArr[!latestAnalogAccum] = 0;
      measureCounter++;
      if (measureCounter >= BLINK_AFTER_MEASURE) measureCounter = 0;
      if (measureCounter == 0) {
        digitalWrite(BUZZER_LED_PIN, HIGH);
      }
      if (measureCounter == 1) {
        digitalWrite(BUZZER_LED_PIN, LOW);
      }

      // Update states and turn on/off buzzer
      updateCellStates();
      updateSafety();
      lastMeasureTime = millis();
    }
    lastInputIndex = inputIndex;
    if (inputIndex < NUM_CELLS-1) {
      inputIndex++;
    }
    else {
      inputIndex = 0;
      if (inputSample < NUM_SAMPLES-1) {
        inputSample++;
      } else {
        inputSample = 0;
      }
    }
  }
}

void updateSafety() {
  if (disconnectedArr[latestAnalogAccum] >= DISCONNECTED_COUNT) {
    tone(BUZZER_PIN, BUZZER_DISCONNECT_FREQ);
    connected = false;
    safe = false;
  } else {
    connected = true;
    safe = true;
    for (int i=0; i<NUM_CELLS; i++) {
      if (cell_states[i] != CELL_SAFE) {
        safe = false;
      }
    }
    if (safe) {
      noTone(BUZZER_PIN);
    } else {
      tone(BUZZER_PIN, BUZZER_FREQ);
    }
  }
}

void updateCellStates() {
  cell_states[0] = new_state(cellVoltageArrs[latestAnalogAccum][0], cellVoltageArrs[latestAnalogAccum][1],
                             disconnectedArr[latestAnalogAccum] >= DISCONNECTED_COUNT, cell_states[0]);
  cell_states[1] = new_state(cellVoltageArrs[latestAnalogAccum][1], cellVoltageArrs[latestAnalogAccum][2],
                             disconnectedArr[latestAnalogAccum] >= DISCONNECTED_COUNT, cell_states[1]);
  cell_states[2] = new_state(cellVoltageArrs[latestAnalogAccum][2], cellVoltageArrs[latestAnalogAccum][0],
                             disconnectedArr[latestAnalogAccum] >= DISCONNECTED_COUNT, cell_states[2]);
}

// returns new state of a cell
cell_state new_state(float voltage, float nextCellVoltage, bool disconnected, cell_state lastState) {
  // Entering unsafe state
  if (disconnected) {
    return CELL_DISCONNECTED;
  } else if (voltage < LOW_VOLTAGE_ENTER_THRESHOLD) {
    return CELL_LOW_VOLTAGE;
  } else if (abs_diff(voltage, nextCellVoltage) > UNBALANCED_ENTER_THRESHOLD) {
    return CELL_UNBALANCED;
  }
  // Exiting unsafe state
  switch (lastState) {
    case CELL_LOW_VOLTAGE:
      if (voltage > LOW_VOLTAGE_EXIT_THRESHOLD) {
        if (abs_diff(voltage, nextCellVoltage) > UNBALANCED_ENTER_THRESHOLD) return CELL_UNBALANCED;
        else return CELL_SAFE;
      }
      return CELL_LOW_VOLTAGE;
    case CELL_UNBALANCED:
      if (lastState == CELL_UNBALANCED && abs_diff(voltage, nextCellVoltage) < UNBALANCED_EXIT_THRESHOLD) {
        return CELL_SAFE;
      }
      return CELL_UNBALANCED;
    case CELL_SAFE:
    case CELL_DISCONNECTED:
    default:
      return CELL_SAFE;
  }
}

float abs_diff(float a, float b) {
  if (a > b) {
    return a - b;
  } else {
    return b - a;
  }
}

// you must implement this function. It is called when the device receives a DeviceUpdate packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_update(uint8_t param, uint32_t value) {
  return ~((uint32_t) 0);
}

// you must implement this function. It is called when the devie receives a DeviceStatus packet.
// the return value is the value field of the DeviceRespond packet hibike will respond with
uint32_t device_status(uint8_t param) {
  return ~((uint32_t) 0);
}

// you must implement this function. It is called with a buffer and a maximum buffer size.
// The buffer should be filled with appropriate data for a DataUpdate packer, and the number of bytes
// added to the buffer should be returned. 
//
// You can use the helper function append_buf.
// append_buf copies the specified amount data into the dst buffer and increments the offset
uint8_t data_update(uint8_t* data_update_buf, size_t buf_len) {
  if (buf_len < (sizeof(safe) + sizeof(connected) + sizeof(cellVoltageArrs[0][0]*NUM_CELLS) + sizeof(cellTotalArr[0]))) {
    return 0;
  }
  uint8_t offset = 0;
  cli();
  append_buf(data_update_buf, &offset, (uint8_t *)&safe, sizeof(safe));
  append_buf(data_update_buf, &offset, (uint8_t *)&connected, sizeof(connected));
  append_buf(data_update_buf, &offset, (uint8_t *)&cellVoltageArrs[latestAnalogAccum][0], sizeof(cellVoltageArrs[0][0])*NUM_CELLS);
  append_buf(data_update_buf, &offset, (uint8_t *)&cellTotalArr[latestAnalogAccum], sizeof(cellTotalArr[0]));
  sei();
  return offset;
}


// You must implement this function.
// It is called when the BBB sends a message to the Smart Device tellinng the Smart Device to disable itself.
// Consult README.md, section 6, to see what exact functionality is expected out of disable.
void device_disable() {

}
