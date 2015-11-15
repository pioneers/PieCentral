# Hibike API

There have been some small updates. Sorry :(

Couple things:
1. There are 2 classes to instantiate for Hibike - Hibike and DeviceContext. Hibike handles interfacing with sensors, while DeviceContext handles sending/recieving data from the user. As such, expect to be working with DeviceContext for the most part.
2. All setter methods are non-blocking, meaning its up to the user to check if the write methods were successful. This can be accomplished by comparing timestamps. Timestamps are initialized as -1, and will be updated for every new value read from the ACK packet returned for the given write request. See Usage for details.
3. All devices will have a specified parameter "dataUpdate" that will correspond to the data written via subscriptions. All other parameters are updated on request. See Usage and Method Summary for getData() for more details.

## DeviceContext
### Constructor Summary

**DeviceContext([configFile])**

Initializes a deviceContext instance, which will store the most up-to-date information on each SmartDevice. 

Input Parameters: 
- configFile, with default value 'hibikeDevices.csv'

Return Value: DeviceContext instance

Blocks: No

### Method Summary

**getData(UID, param)**

Gets the most recently recieved data from the specified device.

Input Parameters:
- UID = "UID string"

Return Value: (value, timestamp)
- value = integer value of latest device reading of param
- timestamp = timestamp of last time param was written to

Blocks: No


**writeValue(UID, param, value)**

Writes a value to the parameter of a particular device, specified by the UID.

Input Parameters:
- UID = integer value of UID
- param = String value of param. List of params for a specfied device can be accessed from getParams()
- value = unsigned integer value to be written

Return Value: None

Blocks: No

**getDelay(UID)**

Get the delay rate for the specified UID. Will fail if the requested UID has not been found active during initialization.

Input Parameters:
- UID = integer representation of device UID

Return Value: int
- delay rate (in milliseconds)

Blocks: No

**subToDevice(UID, delay)**

Subscribes to the specified with the given delay, an int specifying the time between subscriptions in milliseconds. Will fail if a requested UID has not been found active during initialization.

Input Parameters:
- UID = integer representation of device UID
- delay = integer between 0 and 65535

Return Value: None

Blocks: No

**subToDevices(deviceTuples)**

Subscribes to a list of devices. Will fail if a requested UID has not been found active during initialization.

Input Parameters:
- deviceTuples = [(UID_0, delay_0), (UID_1, delay_1), ...]

Return Value: None

Blocks: No

**getParams(uid)**

Returns a list of strings for all parameter names of the specified .

Input Parameters:
- UID = integer repr of device UID

Return Value: list
- ["dataUpdate", "Param1", "Param2", ...]

Blocks: No



## Hibike
### Constructor Summary

**Hibike(deviceContext)**

Initializes the hibike instance and pings all connected devices for UID info.
*Note that Hibike should be treated as a singleton class.*

Input Parameters:
- deviceContext: instance of DeviceContext, to which all data will be read and written to.

Return Value: Hibike instance

Blocks: **Yes**

### Method Summary

**getEnumeratedDevices()**

Returns a list of all active devices detected on setup. Returned list has tuple elements with a UID (as strings) and the associated deviceType (as ints) for convenience.

Input Parameters: None
Return Value: list
- [(UID, deviceType), ...]

Blocks: No


## Usage:

    ### Initialize Hibike ###
    import hibike
    import deviceContext
    import time
    
    context = deviceContext.DeviceContext()
    h = hibike.Hibike(context)


    ### Organize the UIDs however you want ###
    connectedDevices = h.getEnumeratedDevices()


    ### Subscribe to devices as needed ###
    # Retries and wait-times are handled by the user
    subList = zip(deviceUIDs, deviceDelays)
    context.subToDevices(subList)
    
    time.sleep(1)
    
    for i in range(len(deviceUIDs)):
        if context.getDelay(deviceUIDs[i]) != deviceUIDs[i]:
            # handle retries as needed
            print("subscription failed for: "+str(deviceUIDs[i])
    
    context.subToDevice(Potentiometer3_UID, 50)
    while(context.getDelay(Potentiometer3_UID) != 50):
        # handle wait-times as needed
        time.sleep(0.001)
        
        
    ### Get parameters for a certain device ###
    servo_params = context.getParams(servo_UID)
    # servo_params will equal: ["dataUpdate", "servo0", "servo1", "servo2", "servo3"]


    ### Need some data? ###
    device1_reading, device1_reading_timestamp = context.getData(device1_UID, "dataUpdate")


    ### Need to read a device parameter? ###
    _, old_time = context.getData(teamFlag_UID, "status")
    teamFlag_timestamp = old_time
    while teamFlag_timestamp == old_time:
        teamFlag_status, teamFlag_timestamp = context.getData(teamFlag_UID, "status")


    ### Need to write multiple values to a device? ###
    _, old_time1 = context.getData(servo_UID, "servo1")
    _, old_time2 = context.getData(servo_UID, servo_params[2])
    servo_time1 = old_time1
    servo_time2 = old_time2
    timeout = time.time() + 1                           # in seconds
    
    context.writeValue(servo_UID, "servo1", 45)         # write 45 to servo 1
    context.writeValue(servo_UID, servo_params[2], 119) # write 119 to servo 2
    
    # Check if values have been written. Kinda optional, can be run in the background
    while (servo_time1 == old_time1) or (servo_time2 == old_time2):
        servo_val1, servo_time2 = getData(servo_UID, "servo1")
        servo_val2, servo_time2 = getData(servo_UID, "servo2")
        if time.time() > timeout:
            # handle retries as needed
