import { ipcMain } from 'electron';
import LCM from '../../renderer/utils/lcm_ws_bridge';
import { updateTimer,
        updateHeart,
        updateRobot,
        updateMatch }
        from '../../renderer/actions/FieldActions';
import RendererBridge from '../RendererBridge';

class LCMInternals {
  constructor(stationNumber, bridgeAddress) {
    this.lcm = null;
    this.lcmReady = false;
    this.queuedPublish = null;
    this.stationNumber = stationNumber;
    this.bridgeAddress = bridgeAddress;
    console.log(`LCM SN:${this.stationNumber} BA:${this.bridgeAddress}`);
    this.init = this.init.bind(this);
    this.quit = this.quit.bind(this);
    this.lcmPublish = this.lcmPublish.bind(this);
    this.updateStatus = this.updateStatus.bind(this);

    ipcMain.on('LCM_STATUS_UPDATE', this.updateStatus);
  }

  init() {
    this.lcm = new LCM(`ws://${this.bridgeAddress}:8000`);
    this.lcm.on_ready(() => {
      this.lcmReady = true;
      if (this.queuedPublish !== null) {
        this.lcm.publish(this.queuedPublish[0], this.queuedPublish[1]);
        this.queuedPublish = null;
      }
      this.lcm.subscribe('Timer/Time', 'Time', (msg) => {
        RendererBridge.reduxDispatch(updateTimer(msg));
      });
      this.lcm.subscribe('Heartbeat/Beat', 'Heartbeat', (msg) => {
        RendererBridge.reduxDispatch(updateHeart(msg));
      });
      this.lcm.subscribe(`Robot${this.stationNumber}/RobotControl`, 'RobotControl', (msg) => {
        console.log(msg);
        RendererBridge.reduxDispatch(updateRobot(msg));
      });
      this.lcm.subscribe('Timer/Match', 'Match', (msg) => {
        RendererBridge.reduxDispatch(updateMatch(msg));
      });
    });
    this.lcm.on_close(this.init);
  }

  // TODO: Make clearer protocol on how lights should change
  updateStatus(event, data) {
    const connected = data.connectionStatus;
    const ok = data.runtimeStatus;
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
    this.lcmPublish(`StatusLight${this.stationNumber}/StatusLight`, msg);
  }

  lcmPublish(channel, msg) {
    if (this.lcmReady) {
      this.lcm.publish(channel, msg);
    } else {
      console.log('lcm publish queued');
      this.queuedPublish = [channel, msg];
    }
  }

  quit() {
    try {
      this.lcm.ws.close();
    } catch (err) {
      console.log(err);
    }
    ipcMain.removeListener('LCM_STATUS_UPDATE', this.updateStatus);
    this.lcm = null;
  }
}

const LCMObject = {
  LCMInternal: null,
  stationNumber: 4,
  bridgeAddress: 'localhost',
  setup() {
    if (this.LCMInternal !== null) {
      this.LCMInternal.quit();
    }
    this.LCMInternal = new LCMInternals(this.stationNumber, this.bridgeAddress);
    this.LCMInternal.init();
  },
  changeLCMInfo(event, arg) {
    if (arg.stationNumber !== null) {
      LCMObject.stationNumber = arg.stationNumber;
      console.log(`stationNumber set to ${LCMObject.stationNumber}`);
    }

    if (arg.bridgeAddress !== null) {
      LCMObject.bridgeAddress = arg.bridgeAddress;
      console.log(`bridgeAddress set to ${LCMObject.bridgeAddress}`);
    }
  },
};


export default LCMObject;
