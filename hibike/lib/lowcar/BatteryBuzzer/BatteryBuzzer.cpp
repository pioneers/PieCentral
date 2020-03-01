#include "BatteryBuzzer.h"
#include "pdb_defs.h"

// default constructor simply specifies DeviceID and and year to generic constructor
// initalizes helper class objects and pre-existing variables
BatteryBuzzer::BatteryBuzzer () :
  	Device (DeviceID:: BATTERY_BUZZER, 1),
  	disp(SevenSeg(A, B, C, D, E, G, H))
{
	v_cell1 = 0;  // param
	v_cell2 = 0;  // param 4
	v_cell3 = 0;  // param 5
	v_batt = 0;   // param 6
	dv_cell2 = 0; // param 7
	dv_cell3 = 0; // param 8
	vref_guess = 0; // param 9

	triple_calibration = true;

	this->buzzer = 10;
	this->last_check_time = 0; //for loop counter

	this->digitPins[0] = DISP_PIN_1;
	this->digitPins[1] = DISP_PIN_2;
	this->digitPins[2] = DISP_PIN_3;
	this->digitPins[3] = DISP_PIN_4;

	this->last_LED_time = 0;  //Time the last LED switched
	this->sequence = 0; //used to switch states for the display.  Remember that the hangle_8_segment cannot be blocking.

	this->segment_8_run = NORMAL_VOLT_READ;  //0 for the normal voltage readout.  1 for "Clear Calibration".  2 for "New Calibration"
}

uint8_t BatteryBuzzer::device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len)
{
	if (data_buf_len > sizeof(bool)) {
		if (param == IS_UNSAFE) {
			data_buf[0] = is_unsafe();
			return sizeof(bool);
		}
		if (param == CALIBRATED) {
			data_buf[1] = is_calibrated();
			return sizeof(bool);
		}
	}

	if (data_buf_len < sizeof(float) || param >= 8) {
		return 0;
	}

	float *float_buf = (float*) data_buf;

	switch(param) {
		case V_CELL1:
			float_buf[0] = v_cell1;
			break;
		case V_CELL2:
			float_buf[0] = v_cell2;
			break;
		case V_CELL3:
			float_buf[0] = v_cell3;
			break;
		case V_BATT:
			float_buf[0] = v_batt;
			break;
		case DV_CELL2:
			float_buf[0] = dv_cell2;
			break;
		case DV_CELL3:
			float_buf[0] = dv_cell3;
			break;
	}

	data_buf = (uint8_t*) float_buf;
	return sizeof(float);
}

void BatteryBuzzer::device_enable ()
{
	pinMode(buzzer, OUTPUT);

	vref_guess = ADC_REF_NOM; //initial guesses, based on datasheet
	calib[0] = ADC_REF_NOM;
	calib[1] = ADC_REF_NOM;
	calib[2] = ADC_REF_NOM;

	setup_display();
	disp.clearDisp();
	test_display(); //For production to check that the LED display is working
	setup_sensing();
}

void BatteryBuzzer::device_actions()
{
	setup_display();
	disp.clearDisp();

	handle_8_segment();
	SEQ_NUM mode = handle_calibration();
	setup_sensing();

	if ((millis() - last_check_time) > 250) {
		measure_cells();
		last_check_time = millis();
		handle_safety();
	}
	disp.clearDisp();
}

bool BatteryBuzzer::is_calibrated()
{
	//triple calibration arrays are all default values
	if (triple_calibration && (calib[0] == ADC_REF_NOM) && (calib[1]  == ADC_REF_NOM) && (calib[2] == ADC_REF_NOM)) {
		return false;
	}
	//calibration value is set to default
	if (!triple_calibration && (get_calibration() == -1.0)) {
		return false;
	}
	//device is calibrated: no default values
	return true;
}

void BatteryBuzzer::setup_display()
{
	disp.setDigitPins(numOfDigits, digitPins);
	disp.setDPPin(DECIMAL_POINT);  //set the Decimal Point pin to #1
}


void BatteryBuzzer::test_display() //a function to ensure that all outputs of the display are working.
	//On the current PDB, this should display "8.8.8.8."  The library is capable of handling : and ', but the wires are not hooked up to it.
{
	for(int i = 0; i<250; i++) {
		disp.write("8.8.8.8."); //this function call takes a surprising amount of time, probably because of how many characters are in it.
	}
	disp.clearDisp();
}


void BatteryBuzzer::handle_8_segment() //handles the 8-segment display, and prints out the global values.
	//MUST be called in the loop() without any if's
{
	if(segment_8_run == NORMAL_VOLT_READ) {
		//Shows text / numbers of all voltages & then individual cells.
		//Changed every Second
		switch(sequence) {
			case 0: 
				disp.write("ALL");
				break;
			case 1: 
				disp.write(v_batt, 2);
				break;
			case 2: 
				disp.write("CEL.1");
				break;
			case 3: 
				disp.write(v_cell1, 2);
				break;
			case 4: 
				disp.write("CEL.2");
				break;
			case 5: 
				disp.write(dv_cell2, 2);
				break;
			case 6: 
				disp.write("CEL.3");
				break;
			case 7: 
				disp.write(dv_cell3, 2);
				break;
		}

		if (millis() > (last_LED_time + 1000)) { //every second
			sequence = sequence + 1;
			if(sequence == 8) {
				sequence = 0;
			}
			last_LED_time = millis();
		}
	} else if(segment_8_run == CLEAR_CALIB) {
		if(sequence == 0) {
			disp.write("CAL");
		} else if(sequence == 1) {
			disp.write("CLR");
		}

		if (millis() > (last_LED_time + 750)) { //every 3/4 second 
			sequence = sequence + 1;
			if(sequence == 2) {
				start_8_seg_sequence(NORMAL_VOLT_READ); //return to default Programming... showing battery voltages.
			}
			last_LED_time = millis();
		}
	} else if(segment_8_run == NEW_CALIB) {
		if(triple_calibration) {
			switch(sequence) {
				case 0: 
					disp.write("CAL");
					break;
				case 1: 
					disp.write("DONE");
					break;
				case 2:
					disp.write("CAL.1");
					break;
				case 3:
					disp.write(calib[0], 3);
					break;
				case 4:
					disp.write("CAL.2");
					break;
				case 5:
					disp.write(calib[1], 3);
					break;
				case 6:
					disp.write("CAL.3");
					break;
				case 7:
					disp.write(calib[2], 3);
					break;
			}

			if (millis() > (last_LED_time + 750)) { //every 3/4 second
				sequence++;
				if(sequence == 8) {
					start_8_seg_sequence(NORMAL_VOLT_READ); //return to default Programming... showing battery voltages.
				}
				last_LED_time = millis();
			}
		} else {
			switch(sequence) {
				case 0: 
					disp.write("CAL");
					break;
				case 1:
					disp.write("DONE");
					break;
				case 2:
					disp.write("CAL");
					break;
				case 3:
					disp.write(vref_guess, 3);
					break;
			}

			if (millis() > (last_LED_time + 750)) { //every 3/4 second
				sequence++;
				if (sequence == 4) {
					start_8_seg_sequence(NORMAL_VOLT_READ); //return to default Programming... showing battery voltages.
				}
				last_LED_time = millis();
			}
		}
	}
}

void BatteryBuzzer::start_8_seg_sequence(SEQ_NUM sequence_num)
{
	segment_8_run = sequence_num; //rel the display to run the right sequence
	sequence = 0;  //and reset the step in the sequence to zero.
	last_LED_time = millis();
}

void BatteryBuzzer::setup_sensing()
{
	pinMode(ENABLE, OUTPUT);
	pinMode(CALIB_BUTTON, INPUT);

	//for stable (if unknown) internal voltage.
	analogReference(INTERNAL);

	//let's turn enable on, so we can measure the battery voltage.
	digitalWrite(ENABLE, HIGH);

	if(triple_calibration) {
		update_triple_calibration();  //and then update the calibration values I use based on what I now know
	} else {
		float val = get_calibration();
		if(val > 0) { //by convention, val is -1 if there's no calibration.
			vref_guess = val;
		}
	}
}

void BatteryBuzzer::measure_cells() //measures the battery cells. Should call at least twice a second, but preferrably 5x a second.  No use faster.
{
	int r_cell1 = analogRead(CELL1);
	int r_cell2 = analogRead(CELL2);
	int r_cell3 = analogRead(CELL3);

	v_cell1 = float(r_cell1) * (R2 + R5) / R5 * calib[0] / ADC_COUNTS;
	v_cell2 = float(r_cell2) * (R3 + R6) / R6 * calib[1] / ADC_COUNTS;
	v_cell3 = float(r_cell3) * (R4 + R7) / R7 * calib[2] / ADC_COUNTS;

	dv_cell2 = v_cell2 - v_cell1;
	dv_cell3 = v_cell3 - v_cell2;

	v_batt = v_cell3;
}

uint8_t BatteryBuzzer::handle_calibration() //called very frequently by loop.
{
	if (digitalRead(CALIB_BUTTON)) { //I pressed the button, start calibrating.
		float calib_0 = calib[0];
		float calib_1 = calib[1];
		float calib_2 = calib[2];

		//i'm in triple calibration mode, but the calibration array is exactly the same as the datasheet values... which means i haven't been calibrated.
		if(triple_calibration && calib_0 == ADC_REF_NOM && calib_1 == ADC_REF_NOM & calib_2 == ADC_REF_NOM) {
			float vref_new = calibrate();
			calib_0 = calib[0];
			calib_1 = calib[1];
			calib_2 = calib[2];
			write_triple_eeprom(calib_0, calib_1, calib_2);
			return NEW_CALIB;
		} else if(!triple_calibration && get_calibration() == -1.0) { //i'm not in triple calibration mode, and i haven't been calibrated.
			float vref_new = calibrate();
			write_single_eeprom(vref_new);
			return NEW_CALIB;
		} else { //I have already been calibrated with something.  reset it.
			//wait untill the button press goes away.
			//This is to maintain commonality with how calibrate() works.
			{
				delay(1);
			}
			//reset all my calibration values as well, so my calibration values that i'm using are in lockstep with the EEPROM.
			vref_guess = ADC_REF_NOM;
			calib[0] = ADC_REF_NOM;
			calib[1] = ADC_REF_NOM;
			calib[2] = ADC_REF_NOM;

			clear_eeprom();
			return CLEAR_CALIB;
		}
	}
}

//calibrates the device.
//assumes that a 5V line has been put to each battery cell.
//it then calculates its best guess for vref.
float BatteryBuzzer::calibrate()
{
	//wait untill the button press goes away.
	//This is jank debouncing.
	//Have to calibrate AFTER the button is pressed, not while.  Yes, it's wierd.  PCB issue.
	while (digitalRead(CALIB_BUTTON)) {
		delay(1);
	}
	delay(100);

	//ok.  let's assume (for now) that every line has 5V put at it.
	//I want to calculate the best-fit for the true vref.

	//expected voltages, after the resistive dividers.
	float expected_vc1 = EXT_CALIB_VOLT * R5 / (R2 + R5);
	float expected_vc2 = EXT_CALIB_VOLT * R6 / (R3 + R6);
	float expected_vc3 = EXT_CALIB_VOLT * R7 / (R4 + R7);

	int r_cell1 = analogRead(CELL1);
	int r_cell2 = analogRead(CELL2);
	int r_cell3 = analogRead(CELL3);

	//as per whiteboard math.
	float vref1 = ADC_COUNTS / (float(r_cell1)) * R5 / (R2 + R5) * EXT_CALIB_VOLT;
	float vref2 = ADC_COUNTS / (float(r_cell2)) * R6 / (R3 + R6) * EXT_CALIB_VOLT;
	float vref3 = ADC_COUNTS / (float(r_cell3)) * R7 / (R4 + R7) * EXT_CALIB_VOLT;

	//calibration array values are updated.  These are only used if triple calibration is in use.
	calib[0] = vref1;
	calib[1] = vref2;
	calib[2] = vref3;
	//avg all vrefs together to get best guess value
	vref_guess = (vref1 + vref2 + vref3) / 3.0f;
	return vref_guess;
}

//returns if i'm safe or not based on the most recent reading.
//Currently does only over and under voltage protection.  No time averaging.  So will need to be fancier later.
bool BatteryBuzzer::compute_safety() 
{
	bool unsafe;
	// Case 0: Cell voltages are below minimum values.
	if( (v_cell1 < min_cell ) || (dv_cell2 < min_cell) || (dv_cell3 < min_cell) )
	{
		unsafe = true;
		under_volt = true;
	}
	// Case 1: Cell voltages are above maximum values.
	else if((v_cell1 > max_cell ) || (dv_cell2 > max_cell) || (dv_cell3 > max_cell))
	{
		unsafe = true;
	}
	// Case 2: Imbalanced cell voltages.
	else if( (abs(v_cell1 - dv_cell2) > d_cell) || (abs(dv_cell2 - dv_cell3) > d_cell) || (abs(dv_cell3 - v_cell1) > d_cell))
	{
		imbalance = true;
		unsafe = true;
	}
	// Case 3: Previously undervolted, now exceeding exit threshold.  This has the effect of
	// rejecting momentary dips under the undervolt threshold but continuing to be unsafe if hovering close.
	else if(under_volt && (v_cell1 > end_undervolt) && (dv_cell2 > end_undervolt) && (dv_cell3 > end_undervolt) )
	{
		unsafe = false;
		under_volt = false;
	}
	// Case 4: Imbalanced, previously undervolted, and now exceeding exit thresholds.
	else if(imbalance && (abs(v_cell1 - dv_cell2) < end_d_cell) && (abs(dv_cell2 - dv_cell3) < end_d_cell) && (abs(dv_cell3 - v_cell1) < end_d_cell) )
	{
		unsafe = false;
		imbalance = false;
	}
	// Case 5: All is well.
	else
	{
		unsafe = false;
	}
	return unsafe;
}

void BatteryBuzzer::buzz (bool should_buzz)
{
	if(should_buzz) {
		tone(buzzer, NOTE_A5);
	} else {
		noTone(buzzer);
	}
}

void BatteryBuzzer::handle_safety()
{
	unsafe_status = compute_safety(); //Currently, just does basic sensing.  Should get updated.
	buzz(unsafe_status);
}

bool BatteryBuzzer::is_unsafe()
{
	return unsafe_status;
}

float BatteryBuzzer::get_calibration()
{
	if (EEPROM.read(0)=='C' && EEPROM.read(1)=='A' && EEPROM.read(2)=='L' && EEPROM.read(3)==':') {
		//instantiate a float.
		float f = 0.0f;
		EEPROM.get(4,f); //calibration value is stored in location 4
		return f;
	} else {
		return -1.0;
	}
}

//updates the global "calib" array based on EEPROM.
//Calib will contain datasheet values (2.56) if there's no calibration.
//If there is, the appopriate elements will be updated.
void BatteryBuzzer::update_triple_calibration() 
{
	int next_addr = 0;
	for(int i = 1; i<=3; i++) {
		char first = EEPROM.read(next_addr);
		char second = EEPROM.read(next_addr + 1);
		char third = EEPROM.read(next_addr + 2);
		char fourth = EEPROM.read(next_addr + 3);
		char fifth = EEPROM.read(next_addr + 4);

		// Only takes in a valid calibration -  no chance of using partial triple calibration left over in single mode.
		if(first == 'C' && second == 'A' && third == 'L' && fourth == char(i+'0') && fifth == ':') {
			float f = 0.0f; //instantiate a float.
			EEPROM.get(next_addr + 5,f); //calibration value is stored in location 4
			calib[i - 1] = f; // put value into the calibration array
			next_addr = next_addr + 5 + sizeof(float);
		} else {
			return;
		}
	}
}

void BatteryBuzzer::write_single_eeprom(float val)
{
	//Write one-value calibration to eeprom in the following format.
	//This code may not be used in three-calibration mode, which will be standard.
	EEPROM.write(0, 'C');
	EEPROM.write(1, 'A');
	EEPROM.write(2, 'L');
	EEPROM.write(3, ':');

	//Needs arduino 1.6.12 or later.
	EEPROM.put(4, val);
}

void BatteryBuzzer::write_triple_eeprom(float val1, float val2, float val3)
{
	// Write one-value calibration to eeprom in the following format:
	// "CAL1:<float1>CAL2:<float2>CAL3<float3>

	int next_addr = 0;
	for (int i = 1; i <= 3; i++) {
		EEPROM.write(next_addr, 'C');
		next_addr++;
		EEPROM.write(next_addr, 'A');
		next_addr++;
		EEPROM.write(next_addr, 'L');
		next_addr++;
		EEPROM.write(next_addr, char(i+'0'));
		next_addr++;
		EEPROM.write(next_addr,':');
		next_addr++;
		if(i == 1) {
			EEPROM.put(next_addr,val1);
		} else if(i == 2) {
			EEPROM.put(next_addr,val2);
		} else if(i == 3) {
			EEPROM.put(next_addr,val3);
		}
		next_addr = next_addr + sizeof(float);
	}
}

void BatteryBuzzer::clear_eeprom()
{
	// Writes 0 into all positions of the eeprom.
	for (int i = 0 ; i < EEPROM.length() ; i++) {
		EEPROM.write(i, 0);
	}
}
