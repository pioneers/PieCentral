# Overview
**NOTE: This readme is a brief overview. For more in-depth docs on any specific component,
refer to the [wiki](https://github.com/pioneers/daemon/wiki).**

This repo currently contains **Dawn** and **Runtime** in the `dawn/` and `runtime/` folders, respectively.

## Dawn
[Dawn](https://github.com/pioneers/daemon/wiki/Dawn) is a cross-platform frontend for the [PiE](pioneers.berkeley.edu) robotics control system.
It is the applications students will see and use when
programming and testing their robots.

Dawn is a desktop app, but it is written with web technologies and packaged via Electron.

### Download the latest packaged Dawn for your platform:
* [Windows 64-bit](https://storage.googleapis.com/pie-software-builds/latest/dawn-win32-x64.zip)
* [Windows 32-bit](https://storage.googleapis.com/pie-software-builds/latest/dawn-win32-ia32.zip)
* [Mac 64-bit](https://storage.googleapis.com/pie-software-builds/latest/dawn-darwin-x64.zip)
* [Linux 64-bit](https://storage.googleapis.com/pie-software-builds/latest/dawn-linux-x64.zip)
* [Linux 32-bit](https://storage.googleapis.com/pie-software-builds/latest/dawn-linux-ia32.zip)

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
    * Packaging Dawn is done with electron-packager. Run the following from the `dawn` folder:

    ```
    electron-packager . dawn --platform=darwin --arch=x64 --version=0.36.2 --prune
    ```

    Here `--platform` is the target platform (darwin means OSX) and `--version` corresponds to the Electron version. `--prune` removes all dev-dependencies before packaging, since these needlessly increase the packaged filesize. If you use `--prune`, make sure to `npm install` again afterwards to get your dev-dependencies back.

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
