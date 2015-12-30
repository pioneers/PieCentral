#ifndef EX_DEVICE_H
#define EX_DEVICE_H

#include "hibike_device.h"


//////////////// DEVICE UID ///////////////////
hibike_uid_t UID = {
  0xFFFF,                      // Device Type
  0,                      // Year
  UID_RANDOM,     // ID
};
///////////////////////////////////////////////

//////////////// DEVICE DESCRIPTOR ////////////
char* DESCRIPTION = "{"
"    \"deviceID\": \"0xFFFF\","
"    \"deviceName\": \"ExampleDevice\","
"    \"dataFormat\": {"
"        \"formatString\": \"<?BHIQ\","
"        \"parameters\": ["
"            {"
"                \"scalingFactor\": 1.0,"
"                \"machineName\": \"value0\","
"                \"humanName\": \"Example 0\""
"            },"
"            {"
"                \"scalingFactor\": 1.0,"
"                \"machineName\": \"value1\","
"                \"humanName\": \"Example 1\""
"            },"
"            {"
"                \"scalingFactor\": 2.0,"
"                \"machineName\": \"value2\","
"                \"humanName\": \"Example 2\""
"            },"
"            {"
"                \"scalingFactor\": 3.0,"
"                \"machineName\": \"value3\","
"                \"humanName\": \"Example 3\""
"            },"
"            {"
"                \"scalingFactor\": 0.25,"
"                \"machineName\": \"value4\","
"                \"humanName\": \"Example 4\""
"            }"
"        ]"
"    },"
"    \"params\": ["
"        \"dataUpdate\","
"        \"test0\","
"        \"test1\","
"        \"test2\","
"        \"test3\","
"        \"test4\","
"        \"test5\""
"    ]"
"}";
///////////////////////////////////////////////


#define NUM_PARAMS 6


// function prototypes
void setup();
void loop();


#endif /* EX_DEVICE_H */