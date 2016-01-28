# Overview
**NOTE: This readme is a brief overview. For more in-depth docs on any specific component,
refer to the [wiki](https://github.com/pioneers/daemon/wiki).**

This repo currently contains **Dawn** and **Runtime** in the `dawn/` and `runtime/` folders, respectively.

## Dawn
[Dawn](https://github.com/pioneers/daemon/wiki/Dawn) is a cross-platform frontend for the [PiE](pioneers.berkeley.edu) robotics control system. It's also ~~the future~~ a dish soap.
It is the applications students will see and use when
programming and testing their robots.

Dawn is a desktop application, but it is written
using web technologies (primarily ReactJS). This is made possible by a technology
called [Electron](http://electron.atom.io/).

### Quickstart
1. Install Required Software:
    * Get NodeJS or (if you already have it) make sure to update to v5.0.0 (download from the NodeJS website)
    * Get electron: `npm install -g electron-prebuilt`
    * Get electron-packager: `npm install -g electron-packager`
1. Get code and dependencies
    * Pull the latest code from `pioneers/develop`.
    * Enter the dawn directory: `cd dawn`.
    * Install dependencies with npm: `npm install`. Remember to do this step whenever the dependencies change.
1. Start developing:
    * Launch the application: `npm start`. Leave this terminal window running. Dawn should open.
    * To see the effects of changes you make, just hit refresh: `CMD-R` (Mac) or `CTRL-R` (Windows).
1. Package app:
    * Packaging Dawn is done with electron-packager. Run the following from the `dawn` folder:

    ```
    electron-packager . dawn --platform=darwin --arch=x64 --version=0.36.2
    ```

    Here `--platform` is the target platform (darwin means OSX) and `--version` corresponds to the Electron version.

## Runtime
[Runtime](https://github.com/pioneers/daemon/wiki/Runtime)
(formerly griff) is a python based platform for executing student code
and controlling the robot hardware.

### Quickstart
From the 'runtime' directory, run:

1. Install memcached
1. Use pip to install flask, libevent, flask-socketio, and python-memcached
1. `python runtime.py`
1. `memcached -p 12357` (from another terminal window)


## Structure Diagram:
![Dawn Architecture Diagram](https://github.com/pioneers/daemon/wiki/images/DawnArchitecture.png)
