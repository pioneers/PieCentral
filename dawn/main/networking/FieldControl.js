import io from 'socket.io-client';
import { updateRobot, updateHeart, updateMaster } from '../../renderer/actions/FieldActions';
import RendererBridge from '../RendererBridge';
import { Logger } from '../../renderer/utils/utils';
import Ansible from './Ansible';

class FCInternals {
  constructor(stationNumber, bridgeAddress, logger) {
    this.socket = null;
    this.queuedPublish = null;
    this.stationNumber = stationNumber;
    this.bridgeAddress = bridgeAddress;
    this.logger = logger;
    this.logger.log(`Field Control: SN-${this.stationNumber} BA-${this.bridgeAddress}`);
    this.init = this.init.bind(this);
    this.quit = this.quit.bind(this);
  }

  init() {
    this.socket = io(`http://${this.bridgeAddress}:7000`);
    this.socket.on('connect', () => {
      this.logger.log('Connected to Field Control Socket');
      this.socket.on('robot_state', (data) => {
        RendererBridge.reduxDispatch(updateRobot(JSON.parse(data)));
      });
      this.socket.on('heartbeat', () => {
        RendererBridge.reduxDispatch(updateHeart());
      });
      this.socket.on('codes', (data) => {
        if (Ansible.conns[2].socket !== null) {
          Ansible.conns[2].socket.sendFieldControl(JSON.parse(data));
        } else {
          this.logger.log('Trying to send FC Info to Disconnected Robot');
        }
      });
      this.socket.on('master', (data) => {
        RendererBridge.reduxDispatch(updateMaster(JSON.parse(data)));
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

const FCObject = {
  FCInternal: null,
  stationNumber: 4,
  bridgeAddress: 'localhost',
  logger: new Logger('fieldControl', 'Field Control Debug'),
  setup() {
    if (this.FCInternal !== null) {
      this.FCInternal.quit();
    }
    this.FCInternal = new FCInternals(this.stationNumber, this.bridgeAddress, FCObject.logger);
    this.FCInternal.init();
  },
  changeFCInfo(event, arg) {
    if (arg.stationNumber !== null) {
      FCObject.stationNumber = arg.stationNumber;
      FCObject.logger.log(`stationNumber set to ${FCObject.stationNumber}`);
    }

    if (arg.bridgeAddress !== null) {
      FCObject.bridgeAddress = arg.bridgeAddress;
      FCObject.logger.log(`bridgeAddress set to ${FCObject.bridgeAddress}`);
    }
  },
};


export default FCObject;
