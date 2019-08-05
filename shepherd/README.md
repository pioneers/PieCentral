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

Requirements:
1. Field control is the sole source of truth about all that goes on in each match.
   That means Shepherd should produce a detailed audit log that can be read in case.
2. The frontend should minimize the burden placed on the operators.

## Getting Started

```sh
$ npm install
$ npm start
```

The frontend will be running on `http://localhost:8080`.

## Contributing

Documentation should be written in the [JSDoc](https://jsdoc.app/) format.

## Data Model

Due to the real-time nature of field control, we use [RethinkDB](https://www.rethinkdb.com/) to persist our data.

Client state:

```json
{
  "theme": "dark",
  "match": {
    "phase": {
      "remainingDuration": 0,
      "totalDuration": 0
    }
  },
  "teams": [
    {
      "number": 1,
      "name": "HS",
      "host": "127.0.0.1",
      "alliance": "BLUE"
    }
  ]
}
```
