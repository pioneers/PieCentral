#include "battery_buzzer.h"
#include "pdb_defs.h"

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  BATTERY_BUZZER,                      // Device Type
  1,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////


int buzzer = 10;

unsigned long last_check_time = 0; //for the loop counter...

bool calibrated = false;
bool triple_calibration = true; //decide whether to use triple calibration or the simpler single calibration.

float vref_guess = ADC_REF_NOM;  //initial guess, based on datasheet.
float calib[3] = {ADC_REF_NOM,ADC_REF_NOM,ADC_REF_NOM}; //initial guess, based on datasheet.

// normal arduino setup function, you must call hibike_setup() here
void setup() {
  pinMode(buzzer,OUTPUT);

  setup_display();
  test_display();    //For production to check that the LED display is working.
  setup_sensing();

  hibike_setup(); //use default heartbeat rates. look at /lib/hibike/hibike_device.cpp for exact values
}


// normal arduino loop function, you must call hibike_loop() here
// hibike_loop will look for any packets in the serial buffer and handle them

void loop() {
  // do whatever you want here
  // note that hibike will only process one packet per call to hibike_loop()
  // so exessive delays here will affect hibike.
  handle_8_segment();
  handle_calibration();

  if(millis() - last_check_time>250){
    measure_cells();
    last_check_time = millis();
    handle_safety();
  }
  hibike_loop();
}


// You must implement this function.
// It is called when the device receives a Device Write packet.
// Updates param to new value passed in data.
//    param   -   Parameter index
//    data    -   value to write, in little-endian bytes
//    len     -   number of bytes in data
//
//   return  -   size of bytes written on success; otherwise return 0

uint32_t device_write(uint8_t param, uint8_t* data, size_t len) {
  return 0;
}


bool is_calibrated(){
  if(triple_calibration && calib[0] == ADC_REF_NOM && calib[1] == ADC_REF_NOM & calib[2] == ADC_REF_NOM){ // triple calibration arrays are all default values
    return false;
  }
  if(!triple_calibration && get_calibration() == -1.0){ // calibration value is default value
    return false;
  }

  return true; // device is calibrated (no default values)
}

// You must implement this function.
// It is called when the device receives a Device Data Update packet.
// Modifies data to contain the parameter value.
//    param           -   Parameter index
//    data -   buffer to return data in, little-endian
//    len         -   Maximum length of the buffer
//
//    return          -   sizeof(param) on success; 0 otherwise

uint8_t device_read(uint8_t param, uint8_t* data, size_t len) {
  if (len > sizeof(bool)) {
    if(param == IS_UNSAFE){
      data[0] = is_unsafe();
      return sizeof(bool);
    }
    if(param == CALIBRATED){
      data[0] = is_calibrated();
      return sizeof(bool);
    }
  }

  if (len < sizeof(float) || param >= 8){
    return 0;
  }


  float* float_buf = (float *) data;
  if(param == V_CELL1){
    float_buf[0] = v_cell1;
  }
  else if(param == V_CELL2){
    float_buf[0] = v_cell2;
  }
  else if(param == V_CELL3){
    float_buf[0] = v_cell3;
  }
  else if(param == V_BATT){
    float_buf[0] = v_batt;
  }
  else if(param == DV_CELL2){
    float_buf[0] = dv_cell2;
  }
  else if(param == DV_CELL3){
    float_buf[0] = dv_cell3;
  }
  data = (uint8_t*) float_buf;
  return sizeof(float);
}

// You must implement this function.
// It is called when the BBB sends a message to the Smart Device tellinng the Smart Device to disable itself.
// Consult README.md, section 6, to see what exact functionality is expected out of disable.
void device_disable() {

}

