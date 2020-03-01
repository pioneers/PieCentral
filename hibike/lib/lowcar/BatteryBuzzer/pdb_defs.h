#ifndef PDB_DEFS
#define PDB_DEFS

//voltage_sense
//All resistor values (R2-7) are in kOhms
#define R2 10.0
#define R3 30.0
#define R4 51.0
#define R5 10.0
#define R6 10.0
#define R7 10.0

#define ADC_REF_NOM 2.56
#define ADC_COUNTS 1024
#define EXT_CALIB_VOLT 5

#define CELL1 A0
#define CELL2 A1
#define CELL3 A2

#define ENABLE 16
#define CALIB_BUTTON 21

//disp_8
#define A 8
#define B 9
#define C 7
#define D 2
#define E 0
#define G 15
#define H 14
#define DECIMAL_POINT 1

#define DISP_PIN_1 6
#define DISP_PIN_2 5
#define DISP_PIN_3 4
#define DISP_PIN_4 3

// Enumerated values for BatteryBuzzer and VoltageTracker
typedef enum {
	IS_UNSAFE,
	CALIBRATED,
	V_CELL1,
	V_CELL2,
	V_CELL3,
	V_BATT,
	DV_CELL2,
	DV_CELL3,
	VREF_GUESS
} PARAMS;

// Enumerated values for disp_8
typedef enum {
	NORMAL_VOLT_READ,
	CLEAR_CALIB,
	NEW_CALIB
} SEQ_NUM;

#endif
