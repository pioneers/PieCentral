#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"

//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  LIMIT_SWITCH,                      // Device Type
  0,                                 // Year
  UID_RANDOM,                        // ID
};
///////////////////////////////////////////////
char *DESCRIPTION = 
"{"
"    \"deviceID\": \"0x00\","
"    \"deviceName\": \"LimitSwitch\","
"    \"dataFormat\": {"
"        \"formatString\": \"<????\","
"        \"parameters\": ["
"            {"
"                \"scalingFactor\": 1.0,"
"                \"machineName\": \"value0\","
"                \"humanName\": \"Switch 0\""
"            },"
"            {"
"                \"scalingFactor\": 1.0,"
"                \"machineName\": \"value1\","
"                \"humanName\": \"Switch 1\""
"            },"
"            {"
"                \"scalingFactor\": 1.0,"
"                \"machineName\": \"value2\","
"                \"humanName\": \"Switch 2\""
"            },"
"            {"
"                \"scalingFactor\": 1.0,"
"                \"machineName\": \"value3\","
"                \"humanName\": \"Switch 3\""
"            }"
"        ]"
"    },"
"    \"params\": ["
"        \"dataUpdate\""
"    ]"
"}";
#define NUM_SWITCHES 4
#define IN_0 A0
#define IN_1 A1
#define IN_2 A2
#define IN_3 A3

// function prototypes
void setup();
void loop();


#endif /* EX_DEVICE_H */