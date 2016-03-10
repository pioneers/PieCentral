# Overview
**NOTE: This readme is a brief overview. For more in-depth docs on any specific component,
refer to the [wiki](https://github.com/pioneers/daemon/wiki).**

This repo currently contains **Dawn** and **Runtime** in the `dawn/` and `runtime/` folders, respectively.

## Dawn
[Dawn](https://github.com/pioneers/daemon/wiki/Dawn) is a cross-platform frontend for the [PiE](pioneers.berkeley.edu) robotics control system.
It is the applications students will see and use when
programming and testing their robots.

Dawn is a desktop app, but it is written with web technologies and packaged via Electron.

### Experimental builds:
These are **experimental** builds for internal PiE use, and contain the latest features. For the latest
**stable** release, download from [here](http://pioneers.github.io/daemon/).
* [Windows 64-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-win32-x64.zip)
* [Windows 32-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-win32-ia32.zip)
* [Mac 64-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-darwin-x64.zip)
* [Linux 64-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-linux-x64.zip)
* [Linux 32-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-linux-ia32.zip)

### Development Quickstart
1. Install Required Software:
    * Get NodeJS or (if you already have it) make sure to update to v5.0.0 (download from the NodeJS website)
    * Get electron: `npm install -g electron-prebuilt`
1. Get code and dependencies
    * Pull the latest code from `pioneers/develop`.
    * Enter the dawn directory: `cd dawn`.
    * Install dependencies with npm: `npm install`. **Remember to do this step whenever the dependencies change.**
1. Start developing:
    * Start webpack in watch mode: `npm run-script watch`
      * Leave this terminal window running: webpack compiles your code, and automatically recompiles it when it detects changes.
      * **Note**: `npm run-script build` does a similar thing to `npm run-script watch`, but it does not watch for changes, and it builds for production, not development. Use `watch` for development and `build` when you are about to package an app for production.
    * Launch the application: `npm start`.
      * Leave this terminal window running also. Dawn should open.
    * When you make a change, the webpack watcher should automatically recompile your code. To see your changes, hit refresh: `CMD-R` (Mac) or `CTRL-R` (Windows).

### Packaging Dawn
1. Install electron-packager: `npm install -g electron-packager`
1. Build for production: `npm run-script build` (as opposed to `npm run-script watch` during production).
1. Package app:
    * Packaging Dawn is done via a release script. To build for all platforms, run the following from the `dawn` folder:

    ```
    node release.js
    ```
   
   You can build for a specific platform and arch by adding `--platform=<PLATFORM> --arch=<ARCH>`, where `<PLATFORM>` is one of {win32, darwin, linux} and `<ARCH>` is one of {ia32, x64}. To build without pruning (which removes your devDependencies) add `--noprune`.

## Runtime
[Runtime](https://github.com/pioneers/daemon/wiki/Runtime)
(formerly griff) is a python based platform for executing student code
and controlling the robot hardware.

### Quickstart
From the 'runtime' directory, run:

1. Install memcached
1. Use pip to install flask, eventlet, flask-socketio, and python-memcached
1. `python runtime.py`
1. `memcached -p 12357` (from another terminal window)
