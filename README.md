Daemon
======

Daemon is a cross-platform frontend for a robotics control system. It's also the future.

## Quickstart
1. Ensure you have `git`, `npm`. Don't use `brew` to install npm; on OS X (and probably Linux) you can follow the first guide [here](https://gist.github.com/isaacs/579814).
1. `git clone [this repo]`
1. `cd daemon`
1. `npm install -g brunch bower`
1. `npm install` Install node dependencies.
1. `bower install` Install frontend dependencies.
1. `npm run compiler` This will run a watching compiler. You can run a one-time compiler by running `brunch b` instead.
1. `npm run app`
1. `cd app/assets; npm install` Install frontend node dependencies.
1. If you want to work with anything that depends on the radio, you will need to compile your Serialport; see instructions below.

## In-depth Development Setup

You need the following stuff installed on your machine:
- [Node.js & NPM](http://nodejs.org/) (see the instructions for your operating system. Ensure that globally installed NPM modules are in your PATH!)
- Git. Windows users: try [Git Bash](http://git-scm.com/), there is a good usable CLI included which should work with the workflow out-of-the-box. Use Git Bash instead of CMD.exe.
- Linux Users: You may have to do a [weird patch](https://github.com/rogerwang/node-webkit/wiki/The-solution-of-lacking-libudev.so.0).
- [Brunch](http://brunch.io/) and [Bower](http://bower.io/) via a global npm installation: `npm install -g brunch bower`. (You can also install these separately.)
Once you've got those things installed, do
- `npm install` in your directory to install dependencies
- `bower install` in your directory to install frontend. There will sometimes be choices because some packages require different versions of other packages; it's usually ok to just pick the latest version of the package.
- `cd app/assets; npm install` Install frontend node dependencies.
- You should be done with everything except the radio. To compile Serialport to use the radio, see instructions below.

## Developer Tools

- `npm run` to see the various scripts you can run.
- `npm run compiler` assembles your application into `/_public` and watches file changes.
- `npm run app` starts your application locally.
- `npm run deploy` builds your app for windows, osx and linux. the binaries are placed in `/dist` after building.
- `bower install <frontend-module>` for any frontend-related stuff.
- `npm install my-module` **inside of `app/assets`** to install node.js modules.

## Compiling Serialport
[Serialport](https://github.com/voodootikigod/node-serialport) is a Node.js package to interface with hardware serial ports, such as the ones we need to communicate over the radio. There are precompiled binaries online available for Node.js, but not for node-webkit. We have to compile our own.
- First, cd into your `app/assets` folder. You should already have run `npm install` in this folder, but running it again won't hurt.
- `cd node_modules/serialport`.
- Now that we're in the Serialport folder, we need to build it. You should install `node-pre-gyp` and `nw-gyp`: `npm install -g node-pre-gyp nw-gyp`. You could also install them locally, but they need to be on your path.
- Run `node-pre-gyp build --runtime=node-webkit --target=0.10.0`
- You should get a bunch of green output. If you get an error, someone will have to help debug your system.

