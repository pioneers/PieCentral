import io from 'socket.io-client';
import { updateRobot } from '../../renderer/actions/FieldActions';
import RendererBridge from '../RendererBridge';
import { Logger } from '../../renderer/utils/utils';
import { Ansible } from './Ansible';

class LCMInternals {
  constructor(stationNumber, bridgeAddress, logger) {
    this.socket = null;
    this.queuedPublish = null;
    this.stationNumber = stationNumber;
    this.bridgeAddress = bridgeAddress;
    this.logger = logger;
    this.logger.log(`SIO SN:${this.stationNumber} BA:${this.bridgeAddress}`);
    this.init = this.init.bind(this);
    this.quit = this.quit.bind(this);
  }

  init() {
    this.socket = io(`http://${this.bridgeAddress}:7000`);

    this.socket.on('connect', () => {
      this.socket.on('robot_state', (data) => {
        RendererBridge.reduxDispatch(updateRobot(JSON.parse(data)));
      });
      this.socket.on('codes', (data) => {
        Ansible.conns[2].sendFieldControl(JSON.parse(data));
      });
    });
  }

  quit() {
    try {
      this.socket.close();
    } catch (err) {
      this.logger.log(err);
    }
    this.socket = null;
  }
}

const LCMObject = {
  LCMInternal: null,
  stationNumber: 4,
  bridgeAddress: 'localhost',
  logger: new Logger('sio', 'SIO-FC Debug'),
  setup() {
    if (this.LCMInternal !== null) {
      this.LCMInternal.quit();
    }
    this.LCMInternal = new LCMInternals(this.stationNumber, this.bridgeAddress, LCMObject.logger);
    this.LCMInternal.init();
  },
  changeLCMInfo(event, arg) {
    if (arg.stationNumber !== null) {
      LCMObject.stationNumber = arg.stationNumber;
      LCMObject.logger.log(`stationNumber set to ${LCMObject.stationNumber}`);
    }

    if (arg.bridgeAddress !== null) {
      LCMObject.bridgeAddress = arg.bridgeAddress;
      LCMObject.logger.log(`bridgeAddress set to ${LCMObject.bridgeAddress}`);
    }
  },
};


export default LCMObject;
