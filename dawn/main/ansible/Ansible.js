import dgram from 'dgram';
import net from 'net';
import { ipcMain } from 'electron';
import ProtoBuf from 'protobufjs';
import _ from 'lodash';

import RendererBridge from '../RendererBridge';
import {
  ansibleDisconnect,
  notifyChange,
  infoPerMessage,
} from '../../renderer/actions/InfoActions';
import { updatePeripherals } from '../../renderer/actions/PeripheralActions';
import { uploadStatus, stateEnum } from '../../renderer/utils/utils';

let runtimeIP = '192.168.0.200';
let runtimeSocket = null;
let received = false;
const tcpPort = 1234;
const listenPort = 1235;
const sendPort = 1236;
// TODO: Verify if reuseAddr prevents EADDRINUSE
const listenSocket = dgram.createSocket({ type: 'udp4', reuseAddr: true });
const sendSocket = dgram.createSocket({ type: 'udp4', reuseAddr: true });

const dawnBuilder = ProtoBuf.loadProtoFile(`${__dirname}/ansible.proto`);
const DawnData = dawnBuilder.build('DawnData');
const StudentCodeStatus = DawnData.StudentCodeStatus;
const runtimeBuilder = ProtoBuf.loadProtoFile(`${__dirname}/runtime.proto`);
const RuntimeData = runtimeBuilder.build('RuntimeData');
const notificationBuilder = ProtoBuf.loadProtoFile(`${__dirname}/notification.proto`);
const Notification = notificationBuilder.build('Notification');


const tcp = net.createServer((sock) => {
  console.log('Runtime Connected');
  sock.on('end', () => {
    console.log('Runtime Disconnected');
  });
  sock.on('data', (data) => {
    received = true;
    const decoded = Notification.decode(data);
    console.log('Dawn Received TCP');
    if (decoded.header === Notification.Type.STUDENT_RECEIVED) {
      RendererBridge.reduxDispatch(notifyChange(uploadStatus.RECEIVED));
    }
  });
  // TODO: Find why broken pipes might occur
  runtimeSocket = sock;
  if (runtimeSocket) {
    console.log('TCP Socket Verified');
  }
});

tcp.on('error', (err) => {
  console.error('TCP Error');
  throw err;
});

tcp.listen(tcpPort, () => {
  console.log(`Dawn Listening on ${tcpPort}`);
});

function waitRuntimeConfirm(message, count) {
  if (count > 3) {
    console.error('Runtime Failed to Confirm');
    RendererBridge.reduxDispatch(notifyChange(uploadStatus.ERROR));
  } else if (!received) {
    runtimeSocket.write(message, () => {
      console.log(`Runtime Notified: Try ${count + 1}`);
    });
    setTimeout(waitRuntimeConfirm.bind(this, message, count + 1), 1000);
  }
}

/*
 * IPC Connection with Editor.js' upload()
 * When Runtime responds back with confirmation,
 * notifyChange sends received signal (see tcp, received variables)
 */
ipcMain.on('NOTIFY_UPLOAD', () => {
  const message = new Notification({
    header: Notification.Type.STUDENT_SENT,
    console_output: '',
  }).encode().toBuffer();
  if (runtimeSocket == null) {
    console.log('Runtime Hasn\'t Connected Yet');
  } else {
    runtimeSocket.write(message, () => {
      console.log('Runtime Notified: Try 1');
    });
    received = false;
    RendererBridge.reduxDispatch(notifyChange(uploadStatus.SENT));
    waitRuntimeConfirm(message, 0);
  }
});

function buildProto(data) {
  let status = null;
  switch (data.studentCodeStatus) {
    case stateEnum.TELEOP:
      status = StudentCodeStatus.TELEOP;
      break;
    case stateEnum.ESTOP:
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

/*
 * IPC Connection with sagas.js' ansibleGamepads()
 * Sends messages when Gamepad information changes
 * or when 100 ms has passed (with 50 ms cooldown)
 */
ipcMain.on('stateUpdate', (event, data) => {
  const message = buildProto(data).encode().toBuffer();
  console.log('Dawn Sent UDP');
  sendSocket.send(message, sendPort, runtimeIP, (err) => {
    if (err) {
      console.error('UDP Sending Error');
      throw err;
    }
  });
});

/*
 * IPC Connection with ConfigBox.js' saveChanges()
 * Receives new IP Address to send messages to
 */
ipcMain.on('ipAddress', (event, data) => {
  runtimeIP = data.ipAddress;
});

/*
 * Runtime message handler. Sends robot state to store.info
 * and raw sensor array to peripheral reducer
 */
listenSocket.on('message', (msg) => {
  try {
    const data = RuntimeData.decode(msg);
    console.log('Dawn Received UDP');
    RendererBridge.reduxDispatch(infoPerMessage(data.robot_state));
    RendererBridge.reduxDispatch(updatePeripherals(data.sensor_data));
  } catch (e) {
    console.log('Error Decoding UDP');
    throw e;
  }
});

listenSocket.on('error', (err) => {
  console.log('UDP Listening Error');
  listenSocket.close();
  throw err;
});

listenSocket.on('close', () => {
  RendererBridge.reduxDispatch(ansibleDisconnect());
  console.log('UDP Listening Closed');
});

listenSocket.bind(listenPort);
