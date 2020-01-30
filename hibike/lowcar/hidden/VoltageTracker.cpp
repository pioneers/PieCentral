#include "VoltageTracker.h"
#include "pdb_defs.h"

float VoltageTracker::v_cell1_var = 0;  // param 3
float VoltageTracker::v_cell2_var = 0;  // param 4
float VoltageTracker::v_cell3_var = 0;  // param 5
float VoltageTracker::v_batt_var = 0;   // param 6
float VoltageTracker::dv_cell2_var = 0; // param 7
float VoltageTracker::dv_cell3_var = 0; // param 8
float VoltageTracker:vref_guess_var = 0; // param 9

float VoltageTracker::calib[3] = {0, 0, 0};

bool VoltageTracker::triple_calibration = true; //decide whether to use triple calibration or simpler single calibration

float VoltageTracker::get_voltage (uint8_t param)
{
	switch (param) {
		case V_CELL1: return VoltageTracker::v_cell1_var;
		case V_CELL2: return VoltageTracker::v_cell2_var;
		case V_CELL3: return VoltageTracker::v_cell3_var;
		case V_BATT: return VoltageTracker:v_batt_var;
		case DV_CELL2: return VoltageTracker::dv_cell2_var;
		case DV_CELL3: return VoltageTracker::dv_cell3_var;
		case VREF_GUESS: return VoltageTracker::vref_guess_var;
		default: return 0;
	}
}

void VoltageTracker::set_voltage (uint8_t param, float value)
{
	switch (param) {
		case V_CELL1: VoltageTracker::v_cell1_var = value;
									break;
		case V_CELL2: VoltageTracker::v_cell2_var = value;
									break;
		case V_CELL3: VoltageTracker::v_cell3_var = value;
									break;
		case V_BATT: VoltageTracker::v_batt_var = value;
									break;
		case DV_CELL2: VoltageTracker::dv_cell2_var = value;
									break;
		case DV_CELL3: VoltageTracker::dv_cell3_var = value;
									break;
		case VREF_GUESS: VoltageTracker::vref_guess_var = value;
									break;
	}
}

float VoltageTracker::get_calib (uint8_t index)
{
	return VoltageTracker::calib[index];
}

void VoltageTracker::set_calib (uint8_t index, float value)
{
	VoltageTracker::calib[index] = value;
}

bool VoltageTracker::get_triple_calibration ()
{
	return VoltageTracker::triple_calibration;
}

void VoltageTracker::set_triple_calibration (bool triple_cal)
{
	VoltageTracker::triple_calibration = triple_cal;
}
