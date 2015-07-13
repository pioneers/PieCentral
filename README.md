# hibike!
hibike is a lightweight communications protocol designed for the passing of sensor data for the
summer iteration of the PiE Robotics Kit, a.k.a Frank or "Kit Minimum" to some.


## Section 0: A Quick Introduction

We make a few starting assumptions concerning the endpoints of communication. Namely, the device
controlling a sensor is an Arduino of some sort (likely a Micro), and a Beaglebone Black is used as
the central control board of each robot and thus is in charge of communicating with each Arduino.
These two communicate with each other via serial: the Beaglebone running pySerial and the Arduino by
using the built-in serial library. As each Arduino communicates with the Beaglebone on its own separate
port, we conveniently have no need to worry about any race conditions or other problems arising from
concurrency.

The hibike protocol works mostly using subscriptions. The Beaglebone begins communication by sending
a request to the Arduino, which then proceeds to periodically send sensor data to the  Beaglebone at
intervals set by the request message. The latest sensor update received from an Arduino is stored, and
a student polling for sensor data will be given this cached value.

While hibike is designed to mostly use subscriptions, it does offer support for the controlling Beaglebone
to explicitly request data from an Arduino to be returned ASAP.

Finally, we note that code for a COBS-encoding scheme can and should be stolen from the preexisting
Tenshi codebase and then never thought about again.

## Section 1: General Message Structure
All messages have the relatively simple structure of MessageID, ArduinoID, Payload, and checksum as
depicted below. A more complete description of each field is given below the diagram.

    +------------+---------------+---------------------+------------+
    | Message ID | Controller ID |       Payload       |  Checksum  |
    |  (8 bits)  |    (8 bits)   |   (length varies)   |  (8 bits)  |
    +------------+---------------+---------------------+------------+

Message ID - an 8-bit ID specifying the type of message being sent or received. More information
             about each message type is specified in the following sections.

Arduino ID - A UID assigned to each Arduino distributed as part of Kit Minimum. Messages sent from
             the Beaglebone have this field populated with the ID of the Arduino the message is being
             directed to. Messages sent to the Beaglebone have the field populated with the ID of the
             Arduino the message is coming from.

Payload    - Varies wildly depending on the type of message being sent. This will, of course, be
             described in more detail in later sections.

Checksum   - An 8-bit checksum placed at the very end of every message. Really, any checksum scheme
             appending 8-bits to the end of the message will do, but an exceedingly simple one
             recommended exactly for its simplicity is making the checksum the XOR of every other
             byte in the message.

## Section 2: Table summary of message types

    +----+--------------+----------------------------------------------------+------------+
    | ID | Message Type |                     Description                    | Refer to...|
    +------------------------------------------------------------------------+-------------
    | 0  | Subscription | A request for the specified Arduino to return      |  Section 3 |
    |    |   Request    | sensor updates to the Beaglebone at a certain      |            |
    |    |              | frequency.                                         |            |
    +------------------------------------------------------------------------+-------------
    | 1  | Subscription | Sent from Arduino->Beaglebone with either a        |  Section 3 |
    |    |   Response   | confirmation of the received Subscription Request  |            |
    |    |              | or an error code.                                  |            |
    +------------------------------------------------------------------------+-------------
    | 2  | Subscription | A sensor reading update sent from Arduino to       |  Section 4 |
    |    | SensorUpdate | Beaglebone at the frequency set by the most        |            |
    |    |              | recently received SubscriptionRequest.             |            |
    +------------------------------------------------------------------------+-------------
    | 3  | SensorUpdate | Sent from Beaglebone->Arduino to essentially mean  |  Section 5 |
    |    |   Request    | "drop everything that you're doing and give me a   |            |
    |    |              | sensor update NOW"                                 |            |
    +------------------------------------------------------------------------+-------------
    | 4  | SensorUpdate | A response to the message type above. Essentially  |  Section 4 |
    |    |              | identical to a SubscriptionSensorUpdate aside from |            |
    |    |              | its message ID and high priority.                  |            |
    +----+--------------+----------------------------------------------------+------------+
    |0xFF|    Error     | An error of some sort. More details given in the   |  Section 6 |
    |    |              | status code passed in the payload.                 |            |
    +----+--------------+----------------------------------------------------+------------+

## Section 3: Subscription Requests and Responses
A Subscription Request is sent from BeagleBone->Arduino to set up periodic sensor reading updates
from the Arduino. The payload of a SubscriptionRequest is a single unsigned, 32-bit integer that
specifies the delay between sensor readings in milliseconds. Sending a 0 signals the receiving Arduino
to stop sending sensor readings entirely.

Upon receiving a Subscription Request, the Arduino sends back a Subscription Response, which has
payload consisting only of a single 8-bit integer which is 0 upon success and otherwise holds some
nonzero status code. A table of status codes is given below (more error codes will be added as needed).

    +---------+---------------+
    | Status  |    Meaning    |
    +-------------------------+
    |    0    |    SUCCESS    |
    +-------------------------+
    |   0xFF  | Generic Error |
    +-------------------------+

## Section 4: SubscriptionSensorUpdates and SensorUpdates
The Subscription Sensor Update is sent periodically according to the specified delay between messages
given to an Arduino in a Subscription Request. Only one reading is sent per SubscriptionSensorUpdate,
and the format of the payload of a SubscriptionSensorUpdate is as given in the diagram below.

    +---------------+--------------------+------------------------------------+
    |  Sensor Type  |   Reading Length   |               Sensor               |
    |    (8 bits)   |     (16 bits)      |               Reading              |
    +---------------+--------------------+------------------------------------+

What each of these types are for is self-explanatory. Interpretation of the data in each sensor
reading is out of the scope of this protocol, and a section on sensor types will be added in as the
types of sensors provided in the kit are decided upon.

SensorUpdates are formatted identically to SubscriptionSensorUpdates, but they are sent in response
to SensorUpdate requests a single time and not periodically.

## Section 5: Sensor Update Requests
SensorUpdateRequests essentially provide a method of requesting data from the Arduino as soon as
possible as opposed to periodically. This message type has no payload.

Upon receiving a SensorUpdateRequest, an Arduino should respond with a SensorUpdate as quickly as
possible. The formatting of a SensorUpdate is identical to that of a SubscriptionSensorUpdate
described in the section above.

## Section 6: Errors
What this message type is for should be self explanatory. The payload of an error is a simple 8-bit
integer which holds the status code of the error. A table of error codes is given below.

    +---------+---------------+
    | Status  |    Meaning    |
    +-------------------------+
    |   0xFD  |    Invalid    |
    |         |   ArduinoID   |
    +-------------------------+
    |   0xFE  | Checksum Error|
    +-------------------------+
    |   0xFF  | Generic Error |
    +-------------------------+
