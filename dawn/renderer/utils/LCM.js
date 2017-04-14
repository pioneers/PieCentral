import fs from 'fs';
import LCM from './lcm_ws_bridge';
import { updateTimer,
        updateHeart,
        updateRobot,
        updateMatch }
        from '../actions/FieldActions';
import store from '../store';

// TODO: Due to JavaScript's asynchronous nature, verify if this can be read before makeLCM runs.
export let stationNumber;
try {
  stationNumber = parseInt(fs.readFileSync('/opt/driver_station/station_number.txt'), 10);
} catch (err) {
  stationNumber = 2;
}

export let bridgeAddress;
try {
  bridgeAddress = fs.readFileSync('/opt/driver_station/lcm_bridge_addr.txt');
} catch (err) {
  bridgeAddress = 'localhost';
}

console.log(`Station: ${stationNumber}`);
console.log(`Bridge: ${bridgeAddress}`);

let lcm = null;
let lcmReady = false;
let queuedPublish = null;

function lcmPublish(channel, msg) {
  if (lcmReady) {
    lcm.publish(channel, msg);
  } else {
    console.log('lcm publish queued');
    queuedPublish = [channel, msg];
  }
}

function makeLCM() {
  lcm = new LCM(`ws://${bridgeAddress}:8000/`);
  lcm.on_ready(() => {
    lcmReady = true;
    console.log('Connected to LCM Bridge');
    if (queuedPublish !== null) { // TODO: Why is this here?
      lcm.publish(queuedPublish[0], queuedPublish[1]);
      queuedPublish = null;
    }
    lcm.subscribe('Timer/Time', 'Time', (msg) => {
      updateTimer(msg);
    });
    lcm.subscribe('Heartbeat/Beat', 'Heartbeat', (msg) => {
      updateHeart(msg);
    });
    lcm.subscribe(`Robot${stationNumber}/RobotControl`, 'RobotControl', (msg) => {
      updateRobot(msg);
    });
    lcm.subscribe('Timer/Match', 'Match', (msg) => {
      updateMatch(msg);
    });
  });
  lcm.on_close(makeLCM);
}

try {
  makeLCM();
} catch (err) {
  console.log('LCM Unable to start');
}

// TODO: Make clearer protocol on how lights should change
function updateStatus() {
  const state = store.getState();
  const connected = state.info.connectionStatus;
  const ok = state.info.runtimeStatus;
  const msg = {
    __type__: 'StatusLight',
    red: false,
    yellow: false,
    green: false,
    buzzer: false,
  };
  if (connected) {
    if (ok) {
      msg.green = true;
    } else {
      msg.red = true;
    }
  } else {
    msg.red = true;
  }
  lcmPublish(`StatusLight${stationNumber}/StatusLight`, msg);
}

try {
  store.subscribe(updateStatus);
} catch (err) {
  console.log(this);
  console.log(store);
}

export default lcmPublish;
