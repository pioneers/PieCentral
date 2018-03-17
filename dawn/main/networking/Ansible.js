import dgram from 'dgram';
import net from 'net';
import { ipcMain } from 'electron';
import protobuf from 'protobufjs';
import _ from 'lodash';

import RendererBridge from '../RendererBridge';
import { updateConsole } from '../../renderer/actions/ConsoleActions';
import {
  ansibleDisconnect,
  infoPerMessage,
  updateCodeStatus,
} from '../../renderer/actions/InfoActions';
import { updatePeripherals } from '../../renderer/actions/PeripheralActions';
import { robotState, Logger, defaults } from '../../renderer/utils/utils';
import FCObject from './FieldControl';

const DawnData = (new protobuf.Root()).loadSync(`${__dirname}/ansible.proto`, { keepCase: true }).lookupType('DawnData');
const { StudentCodeStatus } = DawnData;

const RuntimeData = (new protobuf.Root()).loadSync(`${__dirname}/runtime.proto`, { keepCase: true }).lookupType('RuntimeData');
const Notification = (new protobuf.Root()).loadSync(`${__dirname}/notification.proto`, { keepCase: true }).lookupType('Notification');

const LISTEN_PORT = 1235;
const SEND_PORT = 1236;
const TCP_PORT = 1234;

function buildProto(data) {
  let status = null;
  switch (data.studentCodeStatus) {
    case robotState.TELEOP:
      status = StudentCodeStatus.TELEOP;
      break;
    case robotState.AUTONOMOUS:
      status = StudentCodeStatus.AUTONOMOUS;
      break;
    case robotState.ESTOP:
      status = StudentCodeStatus.ESTOP;
      break;
    default:
      status = StudentCodeStatus.IDLE;
  }

  const gamepads = _.map(_.toArray(data.gamepads), (gamepad) => {
    const axes = _.toArray(gamepad.axes);
    const buttons = _.map(_.toArray(gamepad.buttons), Boolean);
    return DawnData.Gamepad.create({
      index: gamepad.index,
      axes,
      buttons,
    });
  });

  return DawnData.create({
    student_code_status: status,
    gamepads,
    team_color: (FCObject.stationNumber < 2) ? DawnData.TeamColor.BLUE : DawnData.TeamColor.GOLD,
  });
}

class ListenSocket {
  constructor(logger) {
    this.logger = logger;
    this.statusUpdateTimeout = 0;
    this.socket = dgram.createSocket({ type: 'udp4', reuseAddr: true });
    this.studentCodeStatusListener = this.studentCodeStatusListener.bind(this);
    this.close = this.close.bind(this);
    /*
     * Runtime message handler. Sends robot state to store.info
     * and raw sensor array to peripheral reducer
     */
    this.socket.on('message', (msg) => {
      try {
        const {
          robot_state: stateRobot,
          sensor_data: sensorData,
        } = RuntimeData.decode(msg);
        this.logger.debug(`Dawn received UDP with state ${stateRobot}`);
        RendererBridge.reduxDispatch(infoPerMessage(stateRobot));
        if (stateRobot === RuntimeData.State.STUDENT_STOPPED) {
          if (this.statusUpdateTimeout > 0) {
            this.statusUpdateTimeout -= 1;
          } else {
            this.statusUpdateTimeout = 0;
            RendererBridge.reduxDispatch(updateCodeStatus(robotState.IDLE));
          }
        }
        this.logger.debug(JSON.stringify(sensorData));
        RendererBridge.reduxDispatch(updatePeripherals(sensorData));
      } catch (err) {
        this.logger.log('Error decoding UDP');
        this.logger.debug(err);
      }
    });

    this.socket.on('error', (err) => {
      this.logger.log('UDP listening error');
      this.logger.debug(err);
    });

    this.socket.on('close', () => {
      RendererBridge.reduxDispatch(ansibleDisconnect());
      this.logger.log('UDP listening closed');
    });

    this.socket.bind(LISTEN_PORT, () => {
      this.logger.log(`UDP Bound to ${LISTEN_PORT}`);
    });
    ipcMain.on('studentCodeStatus', this.studentCodeStatusListener);
  }

  studentCodeStatusListener(event, { studentCodeStatus }) {
    if (studentCodeStatus === StudentCodeStatus.TELEOP ||
    studentCodeStatus === StudentCodeStatus.AUTONOMOUS) {
      this.statusUpdateTimeout = 5;
    }
  }

  close() {
    this.socket.close();
    ipcMain.removeListener('studentCodeStatus', this.studentCodeStatusListener);
  }
}

class SendSocket {
  constructor(logger) {
    this.logger = logger;
    this.runtimeIP = defaults.IPADDRESS;
    this.socket = dgram.createSocket({ type: 'udp4', reuseAddr: true });
    this.sendGamepadMessages = this.sendGamepadMessages.bind(this);
    this.ipAddressListener = this.ipAddressListener.bind(this);
    this.close = this.close.bind(this);

    this.socket.on('error', (err) => {
      this.logger.log('UDP sending error');
      this.logger.log(err);
    });

    this.socket.on('close', () => {
      this.logger.log('UDP sending closed');
    });

    ipcMain.on('stateUpdate', this.sendGamepadMessages);

    /*
     * IPC Connection with ConfigBox.js' saveChanges()
     * Receives new IP Address to send messages to.
     */
    ipcMain.on('ipAddress', this.ipAddressListener);
  }

  /*
   * IPC Connection with sagas.js' ansibleGamepads()
   * Sends messages when Gamepad information changes
   * or when 100 ms has passed (with 50 ms cooldown)
   */
  sendGamepadMessages(event, data) {
    const message = DawnData.encode(buildProto(data)).finish();
    this.logger.debug(`Dawn sent UDP to ${this.runtimeIP}`);
    this.socket.send(message, SEND_PORT, this.runtimeIP);
  }

  ipAddressListener(event, { ipAddress }) {
    this.runtimeIP = ipAddress;
  }

  close() {
    this.socket.close();
    ipcMain.removeListener('stateUpdate', this.sendGamepadMessages);
    ipcMain.removeListener('ipAddress', this.ipAddressListener);
  }
}

class TCPSocket {
  constructor(socket, logger) {
    this.requestTimestamp = this.requestTimestamp.bind(this);
    this.sendFieldControl = this.sendFieldControl.bind(this);
    this.close = this.close.bind(this);

    this.logger = logger;
    this.socket = socket;

    this.logger.log('Runtime connected');
    this.socket.on('end', () => {
      this.logger.log('Runtime disconnected');
    });

    this.socket.on('data', (data) => {
      const decoded = Notification.decode(data);
      this.logger.log(`Dawn received TCP Packet ${decoded.header}`);

      switch (decoded.header) {
        case Notification.Type.CONSOLE_LOGGING:
          RendererBridge.reduxDispatch(updateConsole(decoded.console_output));
          break;
        case Notification.Type.TIMESTAMP_UP:
          this.logger.log(`TIMESTAMP: ${_.toArray(decoded.timestamps)}`);
          break;
      }
    });

    /*
     * IPC Connection with Editor.js' upload()
     * When Runtime responds back with confirmation,
     * notifyChange sends received signal (see tcp, received variables)
     */
    ipcMain.on('TIMESTAMP_SEND', this.requestTimestamp);
  }

  requestTimestamp() {
    const TIME = Date.now() / 1000.0;
    const message = Notification.encode(Notification.create({
      header: Notification.Type.TIMESTAMP_DOWN,
      timestamps: [TIME],
    })).finish();

    this.socket.write(message, () => {
      this.logger.log(`Timestamp Requested: ${TIME}`);
    });
  }

  sendFieldControl(data) {
    const rawMsg = {
      header: Notification.Type.GAMECODE_TRANSMISSION,
      gamecode_solutions: data.solutions,
      gamecodes: data.codes,
      rfids: data.rfids,
    };
    const message = Notification.encode(Notification.create(rawMsg)).finish();

    this.socket.write(message, () => {
      this.logger.log(`FC Message Sent: ${rawMsg}`);
    });
  }

  close() {
    this.socket.end();
  }
}

class TCPServer {
  constructor(logger) {
    this.socket = null;
    this.close = this.close.bind(this);
    this.tcp = net.createServer((socket) => {
      this.socket = new TCPSocket(socket, logger);
    });

    this.logger = logger;

    this.tcp.on('error', (err) => {
      this.logger.log('TCP error');
      this.logger.log(err);
    });

    this.tcp.listen(TCP_PORT, () => {
      this.logger.log(`Dawn listening on port ${TCP_PORT}`);
    });
  }

  close() {
    if (this.socket) {
      this.socket.close();
    }

    this.tcp.close();
  }
}

const Ansible = {
  conns: [],
  logger: new Logger('ansible', 'Ansible Debug'),
  setup() {
    this.conns = [
      new ListenSocket(this.logger),
      new SendSocket(this.logger),
      new TCPServer(this.logger),
    ];
  },
  close() {
    this.conns.forEach(conn => conn.close()); // Logger's fs closes automatically
  },
};

export default Ansible;
