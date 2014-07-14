Daemon
======

Daemon is a cross-platform frontend for a robotics control system. It's also the future. 

## Super Quickstart
1. Ensure you have `git`, `npm`. 
1. `npm install -g brunch bower`
1. `git clone [this repo]`
1. `cd daemon`
1. `npm install`
1. `bower install`
1. `npm run compiler`
1. `npm run app`

## Development Setup

You need the following stuff installed on your machine: 
- [Node.js & NPM](http://nodejs.org/) (see the instructions for your operating system. Ensure that globally installed NPM modules are in your PATH!)
- Windows Users: Use a Git Bash or the [PowerShell](http://en.wikipedia.org/wiki/Windows_PowerShell) instead of CMD.exe !
- Linux Users: You may have to do a [symlink](https://github.com/rogerwang/node-webkit/wiki/The-solution-of-lacking-libudev.so.0). 
- Git. (Brunch and Bower depend on Git to work.) Windows users: try [this](http://git-scm.com/), there is a good usable CLI included which should work with the workflow out-of-the-box. The primitive CMD.exe is currently NOT supported. 
- [Brunch](http://brunch.io/) via a global npm installation: `npm install -g brunch`.
- [Bower](http://bower.io/) via a global npm installation: `npm install -g bower`.
- `npm install` in your directory to install dependencies
- `bower install` in your directory to install frontend

## Tools

- `npm run` to see the various scripts you can run. 
- `npm run compiler` assembles your application into `/_public` and watches file changes.
- `npm run app` starts your application locally. 
- `npm run deploy` builds your app for windows, osx and linux. the binaries are placed in `/dist` after building. 
- `bower install <frontend-module>` for any frontend-related stuff.
- `npm install my-module` **inside of `app/assets`** to install node.js modules. 

