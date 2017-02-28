# Overview
Dawn is a cross-platform frontend for the [PiE](https://pioneers.berkeley.edu) robotics control system. It is the
application students will see and use when programming and testing their robots. It is written with web technologies
and packaged via Electron.

### Development Quickstart
1. Install the LTS version of [NodeJS](https://nodejs.org/en/download/)
2. Dawn is a part of the [PieCentral](https://github.com/pioneers/PieCentral) repository, which contains the code for
many of PiE's projects. If you have not already cloned the PieCentral repo, do so now.
3. From the Dawn folder under PieCentral:
    * Run `make watch`. This will pull all the necessary dawn dependencies and start the webpack bundler. Leave
    this running, it will automatically rebundle the app as you make changes.
    * In a separate terminal tab/window, launch the application itself: `make start`. Leave this terminal
    window also running. Dawn should open.
    * When you make a change, the webpack watcher should automatically re-bundle your code. To see your changes in the
    app, you can refresh by clicking `Debug > Reload` from the menu bar.

### Packaging Dawn
**This is only relevant if you are releasing for production.** If you are just developing you can ignore this.

1. Install electron-packager: `npm install -g electron-packager`
2. Build for production: `npm run build` (as opposed to `npm run watch` during production).
3. Package app:
    * Packaging Dawn is done via a release script. To build for all platforms, run the following from the `dawn` folder:

    ```
    node release.js
    ```

   You can build for a specific platform and arch by adding `--platform=<PLATFORM> --arch=<ARCH>`, where `<PLATFORM>`
   is one of {win32, darwin, linux} and `<ARCH>` is one of {ia32, x64}. To build without pruning (which removes your
   devDependencies) add `--noprune`.

### Experimental builds:
These are **experimental** builds for internal PiE use, and contain the latest features. For the latest
**stable** release, download from [here](https://pioneers.github.io/dawn/).
* [Windows 64-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-win32-x64.zip)
* [Windows 32-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-win32-ia32.zip)
* [Mac 64-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-darwin-x64.zip)
* [Linux 64-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-linux-x64.zip)
* [Linux 32-bit](https://storage.googleapis.com/pie-software-builds/experimental/dawn-linux-ia32.zip)
