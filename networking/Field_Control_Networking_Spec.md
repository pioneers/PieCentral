# Field Control Networking Specificiation

## Contents

1. Overview
2. Setting up the Clients and Network
3. Connecting to the Field Control Network
4. Establishing Communication Links
5. Sending Messages

## 1. Overview

A robot interacts with two networks:  the Student network and the Field Control (FC) network.  The former is the network over which students communicate with their robot via provided mini-routers.  The latter--the focus of this spec--is the network over which students' robots interact with FC over the course of a match.

Clients (field control, driver stations, and robots) are assigned static IPs and perform field-related communications over TCP connections.

Robots announce their presence upon joining the FC network.  FC sends out messages to initiate robot-to-driver-station pairing and robot mode changes.  FC listens to heartbeat messages from driver stations.

## 2. Setting Up the Clients and Network

### Client Types

The FC network will have at least six clients, as follows:

- One FC client.  This is the FC computer running the match.  An internet-enabled PiE computer+monitor. 
- One Streaming client.  This is the computer recording/processing/displaying a livestream of the field.  An internet-enabled PiE computer+monitor.
- Four driver station clients.  This acts as the student-robot interface (via Dawn), and as the robot-field control interface (see "Establishing Communication Links").  A wifi-enabled laptop or  computer+monitor.
- Up to four robot clients.  A wifi-enabled Beagle Bone Black (BBB), via wifi dongle.  One per student robot.

Ideally there should be no additional clients; however, in the event that such should be needed, a few IP addresses have been reserved for them. (See "Assigning IP Addresses.")

### Assigning IP Addresses

The Netmask is arbitrarily decided to be 245.245.245.0.  This implies that the subnet prefix, denoted by P, is "245.245.245".

Every client will have a statically assigned IP address.  This is feasible due to the small number of total clients.  Assignment/reservations are as follows:

- P.255:  Broadcast
- P.254:  FC center computer
- P.253-250:  Driver station computers
- P.249:  Streaming computer
- P.248-246:  Spare FC clients
- P.245:  Network gateway (i.e. router)
- P.244-200:  Staff internal robots
- P.199-51:  Unreserved
- P.50-1: Student robots
- P.0:  Netmask

### Software Configurations

#### Network

- **Netmask.**  As mentioned above, this is arbitrarily decided to be P.0.
- **Gateway IP.** This is arbitrarily decided to be P.245.

#### Robot Clients

Each robot is provided a config file mapping a unique identifier (e.g. BBB's MAC address) to a collection of robot-specific settings:

- **Team Number.**  If less than 50, a student robot; if greater than 50, a staff internal robot.
- **IP Address.**  This is derived from team number, as P.TeamNumber.

A robot is also provided a script that takes the robot's unique identifier and this config file, and generates a customized network config file containing the above team-specific settings, as well as static network configurations (netmask, gateway IP).

Qualities and Caveats:

- This config management scheme is desirable due to the ease of updating robots en masse without breaking functionality.  Should any robots need to be reconfigured for any reason, one only need update the config file entries for the affected robot(s). 
- Note, however, that this scheme requires that prior to deployment, _every BBB, student and staff alike, must first be registered_ to some centralized system in order for the config file to be crafted and maintained.  ("Registering" constitutes pairing a MAC addres with a Team Number.)  Known dysfunctional BBBs should also be unregistered, so as to avoid potential config conflicts if accidentally redistributed.

#### FC, Driver Station, and Streaming Clients

**IP Address.** Assigned as described above.

### Internet Access

Both the FC client and Streaming client require internet access; the former to access match scheduling as listed online, and the latter to publish video feed to an online streaming platform (e.g. Twitch).

This is achieved through dual network connections (to both the public internet and FC network), requiring either dual Ethernet ports or an external switch.

## 3. Connecting to the Field Control Network

### Prerequisites

A robot can connect to at most one network at a time, which must be either the Student network or the FC network.  The Student network is to be listed as higher priority than the FC Network.  This can be set in each robot's network config file.

In order to participate in a match, teams temporarily relinquish their routers.

### Rationale 

This results in two desirable guarantees:

1. When not in a match, students will always be able to connect with their robots over the Student network even if the robot is within range of the FC network.
2. When in a match, robots will only have the option of connecting to the FC network (due to router confiscation). 

Note that this may result in robots not in a match to still be connected to the FC network.  However, this is totally fine since the FC client will not be listening to robots not currently tied to a driver station (see "Sending Messages").  Additionally, students can easily restore connection to the Student network by restarting their robot in said network's presence.

## 4. Establishing Communication Links

### TCP

Within each match, the FC network will create/maintain nine TCP connections:

- A connection between the FC client and the Streaming client.  This can persist across matches, and so need to be opened only once per network initialization.
- A connection between the FC client and each Driver Station client.  These can persist across matches, and so need to be opened only once per network initialization.
- A connection beween a Driver Station client and its corresponding Robot client. These must be opened/closed at the start/end of each match (i.e. once the Robot client joins/leaves the FC network and is paired/unpaired with a Driver Station client).

If a FC-to-Driver-Station connection is dropped/becomes invalid, FC is responsible for reestablishing the connection.  If a Driver-Station-to-Robot connection is dropped/becomes invalid, the Driver Station notifies FC; FC then re-sends the pairing message to said Driver Station (see "Sending Messages").

### UDP

The FC network will also support eight UDP connections--two each for Dawn-Runtime communication.  See Dawn/Runtime documentation for further detail.

## 5. Sending Messages

Upon joining the FC network, robots announce their presence to the FC client.

The FC client sends messages to initiate robot-to-driver-station pairing, and to indicate what mode (autonomous, tele-op, etc) the robot is in.   Driver station clients listen accordingly, and pass the message to robots.

To FC, Driver Stations send only a heartbeat, which contains a status value that the FC client can use to verify the intended robot is both paired an in the expected mode.

In further detail:

### From Robots

**Announcing Presence.** Upon joining the FC network, a robot will identify itself to the FC client by sending its unique identifier (MAC address) and Team Number.  This allows the FC client to be aware of the identify of all robots on the network (useful for knowing if the expected teams' robots are in fact connected to the FC network, especially prior to Driver Station pairing).

### From FC

**Robot-to-Driver-Station Pairing.**  Prior to this message, a robot, while connected to the network, is not yet associated with a driver station.  Containing the Team Number of the Robot client with which to pair, the FC client sends this to the Driver Station client, which then opens a connection and begins communication with the first robot to respond.

Once connected, and until the mode changes, a robot's Team Flag will begin blinking.  This will serve as visual confirmation that the intended robots (i.e. the ones currently on the field) are in fact connected.

Failure of a Team Flag to begin blinking may indicate:

- Misconfigured IP address--no robot response (if no robot connection and no off-field blinky Team Flags found).
- Misconfigured IP address--multiple possible robots, incorrect one responded (if robot connection and off-field blinky Team Flag found).
- Broken Team Flag (if robot connection and no off-field blinky Team Flag found).

The match will not proceed until this is externally resolved (e.g. reprogramming the suspected robot(s)'s Beaglebones, replacing Team Flag).

**Mode Changing.**  This message contains an integer indicating whether the robot should be in E-Stopped (0), Disabled (1), Connected (2), Autonomous(3), or Tele-Op (4) mode.  Sent from FC to Driver Station, then Driver Station to Robot.

### From Driver Stations

**Heartbeat.** Upon pairing, the Driver Station begins sending a "heartbeat"--a message containing a single integer between 0 and 4 (inclusive) indicating its robot's mode. If no mode change message has been received yet, it replies Connected (2) by default. Sent from Driver Station to FC.
