#ifndef BATTERY_BUZZER_H
#define BATTERY_BUZZER_H

#include "Device.h"
#include "pitches.h"
#include "pdb_defs.h"
#include <EEPROM.h>
#include <stdint.h>
#include <SevenSeg.h>
#include <Arduino.h>

const int numOfDigits = 4;

class BatteryBuzzer : public Device
{
public:
	bool triple_calibration;
	int buzzer;

	BatteryBuzzer ();

	//overriden functions from Device class; see descriptions in Device.h
	virtual uint8_t device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len);
	virtual void device_enable ();
	virtual void device_actions ();

private:

	/* EEPROM component */

	float get_calibration();
	void update_triple_calibration();
	void write_single_eeprom(float val);
	void write_triple_eeprom(float val1, float val2, float val3);
	void clear_eeprom();

	/* Safety component */

	void handle_safety();
	bool is_unsafe();
	void buzz(bool should_buzz);

	bool unsafe_status;

	const float min_cell = 3.3;
	const float end_undervolt = 3.6; // Exceed this value to remove my undervolt condition.
	bool under_volt;

	const float max_cell = 4.4;

	const float d_cell = 0.3; // Max voltage difference between cells.
	const float end_d_cell = 0.1; //imbalance must be less than this before i'm happy again.
	bool imbalance;

	bool compute_safety();

	/* VoltageSense component */

	void setup_sensing();
	void measure_cells();
	uint8_t handle_calibration();
	float calibrate();

	/* VoltageTracker component */

	float get_voltage (PARAMS param);
	void set_voltage (PARAMS param, float value);

	float get_calib (uint8_t index);
	void set_calib (uint8_t index, float value);

	bool get_triple_calibration();
	void set_triple_calibration(bool triple_cal);

	float v_cell1;  // param 3
	float v_cell2;  // param 4
	float v_cell3;  // param 5
	float v_batt;   // param 6
	float dv_cell2; // param 7
	float dv_cell3; // param 8
	float vref_guess; // param 9

	float calib[3] = {0.0, 0.0, 0.0};

	/* disp_8 component */

	unsigned long last_check_time;

	SevenSeg disp;

	int digitPins[numOfDigits];
	unsigned long last_LED_time;  //Time the last LED switched
	int sequence; //used to switch states for the display.  Remember that the handle_8_segment cannot be blocking.
	SEQ_NUM segment_8_run;  //0 for the normal voltage readout.  1 for "Clear Calibration".  2 for "New Calibration"

	void start_8_seg_sequence(SEQ_NUM sequence_num);
	void handle_8_segment();
	void test_display();
	void setup_display();

	/* BatteryBuzzer component */

	bool is_calibrated ();

};

#endif
