# Dawn
**NOTE: This readme is a brief overview of Dawn. For more in-depth docs on any
specific component, refer to the [wiki](https://github.com/pioneers/daemon/wiki).**

Dawn is a cross-platform frontend and runtime for a robotics control system.
It's also ~~the future~~ a dish soap.

Dawn is divided into two parts with their own subfolders:
- [Dawn App](https://github.com/pioneers/daemon/wiki/Dawn-App) (formerly Daemon) 
  is the actual web application that students use, with two components:
    - The **server**, which will be running on the robot. Developed with NodeJS.
    - The frontend **web client** served by the server, which students will
      see in their web browser. Developed with ReactJS.
- [Dawn Runtime](https://github.com/pioneers/daemon/wiki/Dawn-Runtime) (formerly Griff),
  a python based platform for executing
  student code and controlling the hardware.

## Quickstart
This assumes you have all the required tools installed.

### Starting the app
From the 'app' directory, run:

1. `npm install` (to make sure you have all the dependencies)
1. `gulp build` ( or `gulp watch` to continuously watch for changes )
1. `npm start` (starts the server)

The application should be running on `http://localhost:3000`

### Starting the runtime
From the 'runtime' directory, run:
1. `python runtime.py`
