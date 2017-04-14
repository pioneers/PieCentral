import fs from 'fs';
import LCM from './lcm_ws_bridge';
import { updateTimer,
        updateHeart,
        updateRobot,
        updateMatch,
        updateScore,
        updateLighthouseTimer }
        from '../actions/FieldActions';
import store from '../store';

export const stationNumber = parseInt(fs.readFileSync('/opt/driver_station/station_number.txt'), 10);
export const bridgeAddress = fs.readFileSync('/opt/driver_station/lcm_bridge_addr.txt');
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
    if (queuedPublish !== null) {
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
    lcm.subscribe('LiveScore/LiveScore', 'LiveScore', (msg) => {
      updateScore(msg);
    });
    lcm.subscribe('LighthouseTimer/LighthouseTime', 'LighthouseTime', updateLighthouseTimer);
  });
  lcm.on_close(makeLCM);
}
makeLCM();

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

store.subscribe(updateStatus);

export default lcmPublish;
