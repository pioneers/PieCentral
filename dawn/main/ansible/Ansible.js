import dgram from 'dgram';
import net from 'net';
import { ipcMain } from 'electron';
import ProtoBuf from 'protobufjs';
import _ from 'lodash';

import RendererBridge from '../RendererBridge';
import { updateConsole } from '../../renderer/actions/ConsoleActions';
import {
  ansibleDisconnect,
  notifyChange,
  infoPerMessage,
  updateCodeStatus,
} from '../../renderer/actions/InfoActions';
import { updatePeripherals } from '../../renderer/actions/PeripheralActions';
import { uploadStatus, robotState } from '../../renderer/utils/utils';

const dawnBuilder = ProtoBuf.loadProtoFile(`${__dirname}/ansible.proto`);
const DawnData = dawnBuilder.build('DawnData');
const StudentCodeStatus = DawnData.StudentCodeStatus;
const runtimeBuilder = ProtoBuf.loadProtoFile(`${__dirname}/runtime.proto`);
const RuntimeData = runtimeBuilder.build('RuntimeData');
const notificationBuilder = ProtoBuf.loadProtoFile(`${__dirname}/notification.proto`);
const Notification = notificationBuilder.build('Notification');

const DEFAULT_IP = '192.168.0.200';
const LISTEN_PORT = 1235;
const SEND_PORT = 1236;
const TCP_PORT = 1234;

function buildProto(data) {
  let status = null;
  switch (data.studentCodeStatus) {
    case robotState.TELEOP:
      status = StudentCodeStatus.TELEOP;
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
    const GamepadMsg = new DawnData.Gamepad({
      index: gamepad.index,
      axes,
      buttons,
    });
    return GamepadMsg;
  });

  const message = new DawnData({
    student_code_status: status,
    gamepads,
  });

  return message;
}

class ListenSocket {
  constructor() {
    // TODO: Verify if reuseAddr prevents EADDRINUSE
    this.socket = dgram.createSocket({ type: 'udp4', reuseAddr: true });

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
        console.log('Dawn received UDP');
        RendererBridge.reduxDispatch(infoPerMessage(stateRobot));
        if (stateRobot === RuntimeData.State.STUDENT_STOPPED) {
          RendererBridge.reduxDispatch(updateCodeStatus(robotState.IDLE));
        }
        RendererBridge.reduxDispatch(updatePeripherals(sensorData));
      } catch (err) {
        console.log('Error decoding UDP');
        console.log(err);
      }
    });

    this.socket.on('error', (err) => {
      console.log('UDP listening error');
      console.log(err);
    });

    this.socket.on('close', () => {
      RendererBridge.reduxDispatch(ansibleDisconnect());
      console.log('UDP listening closed');
    });

    this.socket.bind(LISTEN_PORT);
  }

  close() {
    this.socket.close();
  }
}

class SendSocket {
  constructor() {
    this.sendGamepadMessages = this.sendGamepadMessages.bind(this);
    this.ipAddressListener = this.ipAddressListener.bind(this);

    this.runtimeIP = DEFAULT_IP;

    // TODO: Verify if reuseAddr prevents EADDRINUSE
    this.socket = dgram.createSocket({ type: 'udp4', reuseAddr: true });

    this.socket.on('error', (err) => {
      console.error('UDP sending error');
      console.log(err);
    });

    this.socket.on('close', () => {
      console.log('UDP sending closed');
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
    const message = buildProto(data).encode().toBuffer();
    console.log('Dawn sent UDP');
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
  constructor(socket) {
    this.waitRuntimeConfirm = this.waitRuntimeConfirm.bind(this);
    this.tryUpload = this.tryUpload.bind(this);

    this.socket = socket;
    this.received = false;

    console.log('Runtime connected');
    this.socket.on('end', () => {
      console.log('Runtime disconnected');
    });

    this.socket.on('data', (data) => {
      this.received = true;
      const decoded = Notification.decode(data);
      console.log('Dawn received TCP');
      if (decoded.header === Notification.Type.STUDENT_RECEIVED) {
        RendererBridge.reduxDispatch(notifyChange(uploadStatus.RECEIVED));
      } else if (decoded.header === Notification.Type.CONSOLE_LOGGING) {
        console.log(decoded);
        RendererBridge.reduxDispatch(updateConsole(decoded.console_output));
      } else {
        console.log(`${decoded.header}-**************************`);
      }
    });

    /*
     * IPC Connection with Editor.js' upload()
     * When Runtime responds back with confirmation,
     * notifyChange sends received signal (see tcp, received variables)
     */
    ipcMain.on('NOTIFY_UPLOAD', this.tryUpload);
  }

  waitRuntimeConfirm(message, count) {
    if (count > 3) {
      console.error('Runtime failed to confirm');
      RendererBridge.reduxDispatch(notifyChange(uploadStatus.ERROR));
    } else if (!this.received) {
      this.socket.write(message, () => {
        console.log(`Runtime notified: try ${count + 1}`);
      });

      setTimeout(() => {
        this.waitRuntimeConfirm(message, count + 1);
      }, 1000);
    }
  }

  tryUpload() {
    const message = new Notification({
      header: Notification.Type.STUDENT_SENT,
      console_output: '',
    }).encode().toBuffer();

    this.received = false;
    RendererBridge.reduxDispatch(notifyChange(uploadStatus.SENT));
    this.waitRuntimeConfirm(message, 0);
  }

  close() {
    this.socket.end();
    ipcMain.removeListener('NOTIFY_UPLOAD', this.tryUpload);
  }
}

class TCPServer {
  constructor() {
    this.socket = null;
    this.tcp = net.createServer((socket) => {
      this.socket = new TCPSocket(socket);
    });

    this.tcp.on('error', (err) => {
      console.error('TCP error');
      console.log(err);
    });

    this.tcp.listen(TCP_PORT, () => {
      console.log(`Dawn listening on port ${TCP_PORT}`);
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
  setup() {
    this.conns = [
      new ListenSocket(),
      new SendSocket(),
      new TCPServer(),
    ];
  },
  close() {
    this.conns.forEach(conn => conn.close());
  },
};

export default Ansible;
