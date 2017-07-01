# Overview
Dawn is a cross-platform frontend for the [PiE](https://pioneers.berkeley.edu) robotics control system. It is the application students will see and use when programming and testing their robots. It is written with web technologies and packaged via [Electron](https://electron.atom.io/). More details can be found on the [Github wiki](https://github.com/pioneers/PieCentral/wiki).

### Development Quickstart
1. Install the LTS version of [NodeJS](https://nodejs.org/en/download/). For Linux users, your distribution's package repository may be outdated; if so, please look at [alternative sources](https://nodejs.org/en/download/package-manager/).
2. Install [Yarn](https://yarnpkg.com/en/docs/install).
3. Dawn is a part of the [PieCentral](https://github.com/pioneers/PieCentral) repository, which contains the code for many of PiE's projects. If you have not already cloned the PieCentral repo, do so now.
4. From the Dawn folder under PieCentral:
    1. Run `make watch`. This will pull all the necessary dawn dependencies and start the webpack bundler. Leave
    this running, it will try to automatically rebundle the app as you make changes. If it doesn't rebuild after fixing your lint errors, you should kill it and restart.
    2. In a separate terminal tab/window, launch the application itself: `make start`. Leave this terminal window also running. Dawn should open. (Note: For tmux users, do not use tmux for this step due to a [bug in Electron](https://github.com/electron/electron/issues/4236).)
    3. When you make a change, the webpack watcher should automatically re-bundle your code. To see your changes in the app, you can refresh by clicking `Debug > Reload` from the menu bar or enter CMD-R.

### Packaging Dawn for Distribution
1. Once all the features necessary for the next release of Dawn are in place, tag the repository with `dawn/{version}`. A script used in Travis CI will automatically build Dawn for Macs, Windows, and Linux as long as no errors were reported. Built versions will be located in [Releases](https://github.com/pioneers/PieCentral/releases).
2. If ready to ship, bother [Website](mailto:website@pioneers.berkeley.edu) to update the [Software Page](https://pioneers.berkeley.edu/software/).

### Packaging Dawn Locally
**This is only relevant if you are testing a non-development version of Dawn just for yourself.**

1. Install electron-packager: `yarn install electron-packager`
2. Build for production: `yarn run build` (as opposed to `yarn run watch` during production).
3. Package app:
    * Packaging Dawn is done via a release script. To build for all platforms, run the following from the `dawn` folder:

    ```
    node release.js
    ```

   You can build for a specific platform and arch by adding `--platform=<PLATFORM> --arch=<ARCH>`, where `<PLATFORM>`
   is one of {win32, darwin, linux} and `<ARCH>` is one of {ia32, x64}. To build without pruning (which removes your
   devDependencies) add `--noprune`.
