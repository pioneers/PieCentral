# Hibike API

Couple things:
* Runtime need only instantiate one (and only one) Hibike instance. All other setup work for SmartDevice detection and enumeration will happen behind the scenes. It is recommended that Hibike is instantiated at least a couple seconds after robot is powered on.
* All setter methods are non-blocking, meaning its up to the user to check if the write methods were successful. This can be accomplished by comparing timestamps. Timestamps are initialized as -1, and will be updated for every new value read from the ACK packet returned for the given write request. See Usage for details.
* All devices will have a specified parameter "dataUpdate" that will correspond to the data written via subscriptions. All other parameters are updated on request. See Usage and Method Summary for getData() for more details.

## Constructor Summary

### Hibike(contextFile)

Initializes the hibike instance and pings all connected devices for UID info.
*Note that Hibike should be treated as a singleton class.*

Input Parameters:
- contextFile: Absolute filepath to Hibike config file. It is recommended this be left as the default value.

Return Value: Hibike instance

Blocks: **Yes**

## Method Summary

### getData(UID, param, data_format)

Gets the most recently recieved data from the specified device.

Input Parameters:
- UID = "UID string"
- param = String value of param. List of params for a specified device can be accessed from getParams()
- data_format = String value of return type for 'dataUpdate' param only; defaults to "tuple", but can also take "dict" or "int".

Return Value: (value, timestamp)
- value = integer value of latest device reading of param
- timestamp = timestamp of last time param was written to

**Special Case:** If param == 'dataUpdate', value will be a tuple (unless otherwise specified by data_format) of dataUpdate values, one for each actual device connected to the SmartDevice (e.g. a LimitSwitch SD will have 4 actual limit switches connected).

Blocks: No

---

### writeValue(UID, param, value)

Writes a value to the parameter of a particular device, specified by the UID.

Input Parameters:
- UID = integer value of UID
- param = String value of param. List of params for a specfied device can be accessed from getParams()
- value = unsigned integer value to be written

Return Value: None

Blocks: No

---
### getDelay(UID)

Get the delay rate for the specified UID. Will fail if the requested UID has not been found active during initialization.

Input Parameters:
- UID = integer representation of device UID

Return Value: int
- delay rate (in milliseconds)

Blocks: No

---
### subToDevice(UID, delay)

Subscribes to the specified with the given delay, an int specifying the time between subscriptions in milliseconds. Will fail if a requested UID has not been found active during initialization.

Input Parameters:
- UID = integer representation of device UID
- delay = integer between 0 and 65535

Return Value: None

Blocks: No

---
### subToDevices(deviceTuples)

Subscribes to a list of devices. Will fail if a requested UID has not been found active during initialization.

Input Parameters:
- deviceTuples = [(UID_0, delay_0), (UID_1, delay_1), ...]

Return Value: None

Blocks: No

---
### getParams(uid)

Returns a list of strings for all parameter names of the specified .

Input Parameters:
- UID = integer repr of device UID

Return Value: list
- ["dataUpdate", "Param1", "Param2", ...]

Blocks: No

---
### getDeviceName(deviceType)

Returns a string name of a device enum (given in hibike.getEnumeratedDevices). See Usage for details

Input Parameters:
- deviceType = integer enum of a Smart Device

Return Value: String
- String repr of a device, eg: "LimitSwitch", "ServoControl", "Potentiometer"

Blocks: No

---
### getEnumeratedDevices()

Returns a list of all active devices detected on setup. Returned list has tuple elements with a UID (as strings) and the associated deviceType (as ints) for convenience.

Input Parameters: None
Return Value: list
- [(UID, deviceType), ...] where UIDs and deviceTypes are integer values. DeviceType mappings to string names can be accessed via deviceContext.getDeviceName(). See usage section for details.

Blocks: No


## Usage:

    ### Initialize Hibike ###
    import hibike
    import time
    
    h = hibike.Hibike(context)


    ### Organize the UIDs however you want ###
    connectedDevices = h.getEnumeratedDevices()
    
    # device0_name would equal "LimitSwitch"
    device0_name = h.getDeviceTypes[connectedDevices[0][1]] 


    ### Subscribe to devices as needed ###
    # Retries and wait-times are handled by the user
    subList = zip(deviceUIDs, deviceDelays)
    h.subToDevices(subList)
    
    time.sleep(1)   # handle wait-times a needed
    
    for i in range(len(deviceUIDs)):
        if h.getDelay(deviceUIDs[i]) != deviceUIDs[i]:
            # handle retries as needed
            print("subscription failed for: "+str(deviceUIDs[i])
    
    h.subToDevice(Potentiometer3_UID, 50)
    while(context.getDelay(Potentiometer3_UID) != 50):
        time.sleep(0.001)
        
        
    ### Get parameters for a certain device ###
    servo_params = h.getParams(servo_UID)
    # servo_params will equal: ["dataUpdate", "servo0", "servo1", "servo2", "servo3"]


    ### Need some data? ###
    ls_readings, ls_reading_timestamp = h.getData(limitSwitch_UID, "dataUpdate")
	# ls_readings will be a tuple, eg: (1, 0, 1, 0)

    ### Need to read a device parameter? ###
    _, old_time = h.getData(teamFlag_UID, "status")
    tf_timestamp = old_time
    while tf_timestamp == old_time:
        tf_status, tf_timestamp = h.getData(teamFlag_UID, "status")


    ### Need to write multiple values to a device? ###
    _, old_time0 = h.getData(servo_UID, "servo0")
    _, old_time1 = h.getData(servo_UID, servo_params[2])
    servo_time0 = old_time1
    servo_time1 = old_time2
    timeout = time.time() + 1                           # in seconds
    
    h.writeValue(servo_UID, "servo1", 45)         # write 45 to servo 0
    h.writeValue(servo_UID, servo_params[2], 119) # write 119 to servo 1
    
    # Check if values have been written. Kinda optional, 
    # Can be run in the background and or checked at a later time
    while (servo_time0 == old_time0) or (servo_time1 == old_time1):
        servo_val0, servo_time0 = h.getData(servo_UID, "servo0")
        servo_val1, servo_time1 = h.getData(servo_UID, "servo1")
        if time.time() > timeout:
            # handle retries as needed
