# Overview
**NOTE: This readme is a brief overview. For more in-depth docs on any specific component,
refer to the [wiki](https://github.com/pioneers/daemon/wiki).**

[Dawn](https://github.com/pioneers/daemon/wiki/Dawn) is a cross-platform frontend for the [PiE](pioneers.berkeley.edu) robotics control system.
It is the applications students will see and use when
programming and testing their robots.

Dawn is a desktop app, but it is written with web technologies and packaged via Electron.

### Development Quickstart
1. Install Required Software:
    * Install the latest [NodeJS](https://nodejs.org/en/)
    * Once npm is installed, install electron: `sudo npm install -g electron`
1. Get code and dependencies
    * Pull the latest code: `git clone https://github.com/pioneers/dawn`.
    * Get the submodules: `git submodule update  --init --recursive`
    * This should create a `dawn` directory wherever you typed this command. Enter the dawn directory: `cd dawn`.
    * Install dependencies with npm: `npm install`. **Remember to do this step whenever you pull changes!**
1. Start developing (assuming you are in the `dawn` directory):
    * Start webpack in watch mode: `npm run-script watch`
      * Leave this terminal window running: webpack compiles your code, and automatically recompiles it when it detects changes.
      * This also runs a code linter, which will check for errors and incorrect code style.
      * **Note**: `npm run-script build` does a similar thing to `npm run-script watch`, but it does not watch for changes, and it builds for production, not development. Use `watch` for development and `build` when you are about to package an app for production.
    * Launch the application: `npm start`.
      * Leave this terminal window running also. Dawn should open.
    * When you make a change, the webpack watcher should automatically recompile your code. To see your changes, you can refresh by pressing `Debug > Reload` from the menu bar.

### Packaging Dawn
This is only relevant(if you are releasing for production. If you are just developing you can ignore this.

1. Install electron-packager: `npm install -g electron-packager`
1. Build for production: `npm run-script build` (as opposed to `npm run-script watch` during production).
1. Package app:
    * Packaging Dawn is done via a release script. To build for all platforms, run the following from the `dawn` folder:

    ```
    node release.js
    ```
   
   You can build for a specific platform and arch by adding `--platform=<PLATFORM> --arch=<ARCH>`, where `<PLATFORM>` is one of {win32, darwin, linux} and `<ARCH>` is one of {ia32, x64}. To build without pruning (which removes your devDependencies) add `--noprune`.

### Experimental builds:
These are **experimental** builds for internal PiE use, and contain the latest features. For the latest
**stable** release, download from [here](http://pioneers.github.io/daemon/).
* [Windows 64-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-win32-x64.zip)
* [Windows 32-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-win32-ia32.zip)
* [Mac 64-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-darwin-x64.zip)
* [Linux 64-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-linux-x64.zip)
* [Linux 32-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-linux-ia32.zip)
