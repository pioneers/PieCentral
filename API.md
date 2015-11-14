# Hibike API

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

Return Value: int
- latest device reading of param

Blocks: No


**writeValue(UID, param, value)**

Writes a value to the parameter of a particular device, specified by the UID.

Input Parameters:
- UID = integer value of UID
- param = String value of param. List of params for a specfied device can be accessed from getDeviceParams()
- value = unsigned integer value to be written

Return Value: None

Blocks: No

**getDelay(UID)**



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


## Hibike
### Constructor Summary

**Hibike()**

Initializes the hibike instance and pings all connected devices for UID info.
*Note that Hibike should be treated as a singleton class.*

Input Parameters: None

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
    h = hibike.Hibike()

    ### Organize the UIDs however you want ###
    connectedDevices = h.getEnumeratedDevices()

    ### Subscribe to devices as needed ###
    subList = zip(deviceUIDs, deviceDelays)
    h.subToDevices(subList)

    ### Need some data? ###
    device1_reading = h.getData(device1_UID)

    ### Need to read a device parameter? ###
    device2_param0 = h.readValue(device2_UID, 0)

    ### Need to write a device's parameter? ###
    h.writeValue(device2_UID, 0, 0xff)
