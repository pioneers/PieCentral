# Hibike API

## Constructor Summary

**Hibike()**

Initializes the hibike instance and pings all connected devices for UID info.
*Note that Hibike should be treated as a singleton class.*

Input Parameters: None
Return Value: None
Blocks: **Yes**

## Method Summary

**getEnumeratedDevices()**

Returns a list of all active devices detected on setup. Returned list has tuple elements with a UID (as strings) and the associated deviceType (as ints) for convenience.

Input Parameters: None
Return Value: list
- [(UID, deviceType), ...]

Blocks: No

**subscribeToDevices(deviceList)**

Subscribes to all specified devices with the given delay, an int specifying the subscription rate in milliseconds. Will fail if a requested UID has not been found active during initialization. May also fail if subscription requests fail.

Input Parameters: 
- deviceList = [(UID, delay), ...]

Return Value: int
- 0 = operation successful
- 1 = failed to subscribe to a device
- 2 = given an unrecognized UID

Blocks: **Yes**

**getData(UID)**

Gets the most recently recieved data from the specified device.

Input Parameters:
- UID = "UID string"

Return Value: int
- latest device reading

Blocks: No

**readValue(UID, param)**

Looks up the specified parameter from the state of the specified device. Note that these values are not cached and must be looked up on demand.

Input Parameters:
- UID = "UID string"
- param = int specfying which parameter (enumerated elsewhere)

Return Value: int
- current parameter value

Blocks: **Yes**

**writeValue(UID, param, value)**

Writes a specified value to the given parameter of a the given device.

Input Parameters:
- UID = "UID string"
- param = in specifying which parameter (enumerated elsewhere)
- value = int of the data to be written to the parameter

Return Value: int
- 0 = operation successful
- 1 = operation failed

Blocks: **Yes**

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
