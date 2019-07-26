# Shepherd

Shepherd is the PiE Robotics field control stack, consisting of:
* A dashboard for running and monitoring matches
* A scoreboard and other competitor-facing UIs (like perk selection)
* Field sensors and actuators
* A backend server that coordinates all of the above

## Architecture

Shepherd, a heavily event-driven application, is primarily written in JavaScript:
* All frontend pages are bundled using Webpack + React into static assets (HTML, JS, font files, etc).
  The frontend expects to communicate asynchronously with the backend server.
* The backend server uses ExpressJS to expose APIs for interacting with the field.

## Getting Started

To develop,
```sh
$ npm run develop
```

To deploy,
```sh
$ npm run build
```
