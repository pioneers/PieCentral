#include "example_device.h"

#include "Arduino.h" 

// each device is responsible for keeping track of it's own params
// This must match the table in hibikeDevices.json
bool kumiko;
uint8_t hazuki;
int8_t sapphire;
uint16_t reina;
int16_t asuka;
uint32_t haruka;
int32_t kaori;
uint64_t natsuki;
int64_t yuko;
float  mizore;
float nozomi;
uint8_t shuichi;
uint16_t takuya;
uint32_t riko;
uint64_t aoi;
float noboru;


// normal arduino setup function, you must call hibike_setup() here
void setup() {
  hibike_setup(); //use default heartbeat rates. look at /lib/hibike/hibike_device.cpp for exact values
  
  //alternatively, you can set up custom heartbeat periods:
  //hibike_setup(750, 100); //750 ms without heartbeat to disable, ask for heartbeats every 100 ms.
  //set either (or both) of these constants to zero to disable the particular functionality.
}


// normal arduino loop function, you must call hibike_loop() here
// hibike_loop will look for any packets in the serial buffer and handle them
// hibike_loop will call device_write and device_read

void loop() {
  // do whatever you want here
  // note that hibike will only process one packet per call to hibike_loop()
  // so exessive delays here will affect hibike.
  //don't change Kumiko.

  hazuki += 0;
  sapphire += 1;
  reina += 2;
  asuka += 3;
  haruka += 4;
  kaori += 5;
  natsuki += 6;
  yuko += 7;
  mizore += 8.8;
  nozomi += 9.9;
  shuichi += 10;
  takuya += 11;
  riko += 12;
  aoi += 13;
  noboru += 14.14;

  hibike_loop();
}


// You must implement this function.
// It is called when the device receives a Device Write packet from the BBB.
// Updates param to new value passed in data.
// There must be a check that there are enough bytes to write the desired
// parameter value into data a.k.a len < sizeof(value)
//
//    param   -   Parameter index
//    data    -   buffer to get the value from, in little-endian bytes
//    len     -   size of the buffer for overflow checking
//
//   return   -   number of bytes read from data on success; otherwise return 0

uint32_t device_write(uint8_t param, uint8_t* data, size_t len) {
  switch (param) {
    case KUMIKO:
      if (len < sizeof(kumiko)) {
        return 0;
      }
      kumiko = ((bool*)data)[0];
      return sizeof(kumiko);
      break;

    case HAZUKI:
      if (len < sizeof(hazuki)) {
        return 0;
      }
      hazuki = ((uint8_t*)data)[0];;
      return sizeof(hazuki);
      break;
    case SAPPHIRE:
      if (len < sizeof(sapphire)) {
        return 0;
      }
      sapphire = ((int8_t*)data)[0];
      return sizeof(sapphire);
      break;
    case REINA:
      if (len < sizeof(reina)) {
        return 0;
      }
      reina = ((uint16_t*)data)[0];
      return sizeof(reina);
      break;
    case ASUKA:
      if (len < sizeof(asuka)) {
        return 0;
      }
      asuka = ((int16_t*)data)[0];
      return sizeof(asuka);
      break;
    case HARUKA:
      if (len < sizeof(haruka)) {
        return 0;
      }
      haruka = ((uint32_t*)data)[0];
      return sizeof(haruka);
      break;
    case KAORI:
      if (len < sizeof(kaori)) {
        return 0;
      }
      kaori = ((int32_t*)data)[0];
      return sizeof(kaori);
      break;
    case NATSUKI:
      if (len < sizeof(natsuki)) {
        return 0;
      }
      natsuki = ((uint64_t*)data)[0];
      return sizeof(natsuki);
      break;
    case YUKO:
      if (len < sizeof(yuko)) {
        return 0;
      }
      yuko = ((int64_t*)data)[0];
      return sizeof(yuko);
      break;
    case MIZORE:
      if (len < sizeof(mizore)) {
        return 0;
      }
      mizore = ((float*)data)[0];
      break;
    case NOZOMI:
      if (len < sizeof(nozomi)) {
        return 0;
      }
      nozomi = ((float*)data)[0];
      return sizeof(nozomi);
      break;
    case SHUICHI:
      //not writable
      return 0;
      break;
    case TAKUYA:
      if (len < sizeof(takuya)) {
        return 0;
      }
      takuya = ((uint16_t*)data)[0];
      return sizeof(takuya);
      break;
    case RIKO:
      //not writable
      return 0;
      break;
    case AOI:
      if (len < sizeof(aoi)) {
        return 0;
      }
      aoi = ((uint64_t*)data)[0];
      return sizeof(aoi);
      break;
    case NOBORU:
      //not writable.
      return 0;
      break;
    default:
      return 0;
  }
  return 0;
}


// You must implement this function.
// It is called when the device wants to send data to the BBB.
// Modifies data to contain the parameter value.
//    param   -   Parameter index
//    data    -   buffer to return data in, little-endian
//    len     -   size of the buffer for overflow checking
//
//    return  -   number of bytes writted to data on success; 0 otherwise
uint8_t device_read(uint8_t param, uint8_t* data, size_t len) {
  switch (param) 
  {
    case KUMIKO:
      if (len < sizeof(kumiko)) {
        return 0;
      }
      ((bool*)data)[0] = kumiko;
      return sizeof(kumiko);
      break;
    case HAZUKI:
      if (len < sizeof(hazuki)) {
        return 0;
      }
      ((uint8_t*)data)[0] = hazuki;
      return sizeof(hazuki);
      break;
    case SAPPHIRE:
      if (len < sizeof(sapphire)) {
        return 0;
      }
      ((int8_t*)data)[0] = sapphire;
      return sizeof(sapphire);
      break;
    case REINA:
      if (len < sizeof(reina)) {
        return 0;
      }
      ((uint16_t*)data)[0] = reina;
      return sizeof(reina);
      break;
    case ASUKA:
      if (len < sizeof(asuka)) {
        return 0;
      }
      ((int16_t*)data)[0] = asuka;
      return sizeof(asuka);
      break;
    case HARUKA:
      if (len < sizeof(haruka)) {
        return 0;
      }
      ((uint32_t*)data)[0] = haruka;
      return sizeof(haruka);
      break;
    case KAORI:
      if (len < sizeof(kaori)) {
        return 0;
      }
      ((int32_t*)data)[0] = kaori;
      return sizeof(kaori);
      break;
    case NATSUKI:
      if (len < sizeof(natsuki)) {
        return 0;
      }
      ((uint64_t*)data)[0] = natsuki;
      return sizeof(natsuki);
      break;
    case YUKO:
      if (len < sizeof(yuko)) {
        return 0;
      }
      ((int64_t*)data)[0] = yuko;
      return sizeof(yuko);
      break;
    case MIZORE:
      if (len < sizeof(mizore)) {
        return 0;
      }
      ((float*)data)[0] = mizore;
      return sizeof(mizore);
      break;
    case NOZOMI:
      if (len < sizeof(nozomi)) {
        return 0;
      }
      ((float*)data)[0] = nozomi;
      return sizeof(nozomi);
      break;
    case SHUICHI:
      if (len < sizeof(shuichi)) {
        return 0;
      }
      ((uint8_t*)data)[0] = shuichi;
      return sizeof(shuichi);
      break;
    case TAKUYA:
      //not readable
      return 0;
      break;
    case RIKO:
      if (len < sizeof(riko)) {
        return 0;
      }
      ((uint32_t*)data)[0] = riko;
      return sizeof(riko);
      break;
    case AOI:
      //not readable.
      return 0;
      break;
    case NOBORU:
      if (len < sizeof(noboru)) {
        return 0;
      }
      ((float*)data)[0] = noboru;
      return sizeof(noboru);
      break;
    default:
      return 0;
  }
  return 0;
}


// You must implement this function.
// It is called when the BBB sends a message to the Smart Device tellinng the Smart Device to disable itself.
// Consult README.md, section 6, to see what exact functionality is expected out of disable.
void device_disable() {
  kumiko = false;

  hazuki = 0;
  sapphire = 0;
  reina = 0;
  asuka = 0;
  haruka = 0;
  kaori = 0;
  natsuki = 0;
  yuko = 0;
  mizore = 0;
  nozomi = 0;
  shuichi = 0;
  takuya = 0;
  riko = 0;
  aoi = 0;
  noboru = 0;

}
