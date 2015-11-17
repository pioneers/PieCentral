# Hibike API

There have been some changes. Sorry :(

Couple things:
* There are 2 classes to instantiate for Hibike - Hibike and DeviceContext. Hibike handles interfacing with sensors, while DeviceContext handles sending/recieving data from the user. As such, expect to be working with DeviceContext for the most part.
* All setter methods are non-blocking, meaning its up to the user to check if the write methods were successful. This can be accomplished by comparing timestamps. Timestamps are initialized as -1, and will be updated for every new value read from the ACK packet returned for the given write request. See Usage for details.
* All devices will have a specified parameter "dataUpdate" that will correspond to the data written via subscriptions. All other parameters are updated on request. See Usage and Method Summary for getData() for more details. Note that for devices like servos, dataUpdate will never be written to.

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

**getDeviceName(deviceType)**

Returns a string name of a device enum (given in hibike.getEnumeratedDevices). See Usage for details

Input Parameters:
- deviceType = integer enum of a Smart Device

Return Value: String
- String repr of a device, eg: "LimitSwitch", "ServoControl", "Potentiometer"

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
- [(UID, deviceType), ...] where UIDs and deviceTypes are integer values. DeviceType mappings to string names can be accessed via deviceContext.getDeviceName(). See usage section for details.

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
    
    # device0_name would equal "LimitSwitch"
    device0_name = comtext.getDeviceTypes[connectedDevices[0][1]]	


    ### Subscribe to devices as needed ###
    # Retries and wait-times are handled by the user
    subList = zip(deviceUIDs, deviceDelays)
    context.subToDevices(subList)
    
    time.sleep(1)	# handle wait-times a needed
    
    for i in range(len(deviceUIDs)):
        if context.getDelay(deviceUIDs[i]) != deviceUIDs[i]:
            # handle retries as needed
            print("subscription failed for: "+str(deviceUIDs[i])
    
    context.subToDevice(Potentiometer3_UID, 50)
    while(context.getDelay(Potentiometer3_UID) != 50):
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
    _, old_time0 = context.getData(servo_UID, "servo0")
    _, old_time1 = context.getData(servo_UID, servo_params[2])
    servo_time0 = old_time1
    servo_time1 = old_time2
    timeout = time.time() + 1                           # in seconds
    
    context.writeValue(servo_UID, "servo1", 45)         # write 45 to servo 0
    context.writeValue(servo_UID, servo_params[2], 119) # write 119 to servo 1
    
    # Check if values have been written. Kinda optional, 
    # Can be run in the background and or checked at a later time
    while (servo_time0 == old_time0) or (servo_time1 == old_time1):
        servo_val0, servo_time0 = getData(servo_UID, "servo0")
        servo_val1, servo_time1 = getData(servo_UID, "servo1")
        if time.time() > timeout:
            # handle retries as needed
