# Overview
**NOTE: This readme is a brief overview. For more in-depth docs on any specific component,
refer to the [wiki](https://github.com/pioneers/daemon/wiki).**

This repo currently contains **Dawn** and **Runtime** in the `app/` and `runtime/` folders, respectively.

## Dawn
[Dawn](https://github.com/pioneers/daemon/wiki/Dawn) is a cross-platform frontend for the [PiE](pioneers.berkeley.edu)
robotics control system.
It's also ~~the future~~ a dish soap. It is the applications students will see and use when
programming and testing their robots. Dawn is divided into two components:
  - The **server**, which will be running on the robot. Developed with NodeJS.
  - The frontend **web client** served by the server, which students will
    see in their web browser. Developed with ReactJS.

### Quickstart
This assumes you have all the required tools installed.
From the 'app' directory, run:

1. `npm install` (to make sure you have all the dependencies)
1. `gulp build` ( or `gulp watch` to continuously watch for changes )
1. `npm start` (starts the server)

The application should be running on `http://localhost:3000`

## Runtime
[Runtime](https://github.com/pioneers/daemon/wiki/Runtime)
(formerly griff) is a python based platform for executing student code
and controlling the robot hardware.

### Quickstart
From the 'runtime' directory, run:

1. `python runtime.py`
 

## Structure Diagram:
![Dawn Architecture Diagram](https://github.com/pioneers/daemon/wiki/images/DawnArchitecture.png)
