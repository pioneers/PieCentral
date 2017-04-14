import LCM from './lcm_ws_bridge'
import FieldActions from '../actions/FieldActions.js'
import RobotInfoStore from '../stores/RobotInfoStore'

import fs from 'fs';
export const stationNumber = parseInt(fs.readFileSync('/opt/driver_station/station_number.txt'));
export const bridgeAddress = fs.readFileSync('/opt/driver_station/lcm_bridge_addr.txt');
console.log("station: " + stationNumber);
console.log("bridge: " + bridgeAddress);


let lcm = null;
let lcm_ready = false;
let queued_publish = null;

function makeLCM(){
    lcm = new LCM('ws://' + bridgeAddress + ':8000/');
    function subscribeAll() {
        lcm_ready = true;
        console.log('Connected to LCM Bridge');
        if (queued_publish !== null) {
            lcm.publish(queued_publish[0], queued_publish[1]);
            queued_publish = null;
        }

        lcm.subscribe("Timer/Time", "Time", function(msg) {
           FieldActions.updateTimer(msg)
        });
        lcm.subscribe("Heartbeat/Beat", "Heartbeat", function(msg) {
           FieldActions.updateHeart(msg)
        });
        lcm.subscribe("Robot" + stationNumber + "/RobotControl", "RobotControl", function(msg) {
            FieldActions.updateRobot(msg)
        });
        lcm.subscribe("Timer/Match", "Match", function(msg) {
            FieldActions.updateMatch(msg)
        });
        lcm.subscribe("LiveScore/LiveScore", "LiveScore", function(msg) {
            FieldActions.updateScore(msg)
        });
        lcm.subscribe("LighthouseTimer/LighthouseTime", "LighthouseTime", FieldActions.updateLighthouseTimer)
    }
    lcm.on_ready(subscribeAll);
    lcm.on_close(makeLCM);
}
makeLCM();

const updateStatus = function() {
    const connected = RobotInfoStore.getConnectionStatus();
    const ok = RobotInfoStore.getRuntimeStatus();
    let msg = {__type__: 'StatusLight', red: false, yellow: false, green: false, buzzer: false};
    if (connected) {
        if (ok) {
            msg.green = true;
        } else {
            msg.red = true;
        }
    } else {
        msg.red = true;
    }
    lcm_publish("StatusLight" + stationNumber + "/StatusLight", msg)

}
RobotInfoStore.on("change", updateStatus);
updateStatus();

function lcm_publish(channel, msg) {
    if (lcm_ready) {
        lcm.publish(channel, msg)
    } else {
        console.log("lcm publish queued");
        queued_publish = [channel, msg];
    }
}


export default lcm_publish;
