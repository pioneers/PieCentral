import { ipcMain } from 'electron';
import ProtoBuf from 'protobufjs';
import dgram from 'dgram';
import net from 'net';
import _ from 'lodash';
import {
  ansibleDisconnect,
  notifyChange,
  infoPerMessage,
} from '../../renderer/actions/InfoActions';
import { updatePeripherals } from '../../renderer/actions/PeripheralActions';
import { uploadStatus, stateEnum } from '../../renderer/utils/utils';
import RendererBridge from '../RendererBridge';

let runtimeIP = 'localhost';  // '192.168.128.22';
const tcpPort = 1234;
const clientPort = 1236; // send port
const serverPort = 1235; // receive port
const client = dgram.createSocket('udp4'); // sender
const server = dgram.createSocket('udp4'); // receiver


const dawnBuilder = ProtoBuf.loadProtoFile(`${__dirname}/ansible.proto`);
const DawnData = dawnBuilder.build('DawnData');
const StudentCodeStatus = DawnData.StudentCodeStatus;

const runtimeBuilder = ProtoBuf.loadProtoFile(`${__dirname}/runtime.proto`);
const RuntimeData = runtimeBuilder.build('RuntimeData');
const notificationBuilder = ProtoBuf.loadProtoFile(`${__dirname}/notification.proto`);
const Notification = notificationBuilder.build('Notification');

let runtimeSocket = null;
let received = false;

const tcp = net.createServer((sock) => {
  console.log('Runtime Connected');
  sock.on('end', () => {
    console.log('Runtime Disconnected');
  });
  sock.on('data', (data) => {
    received = true;
    const decoded = Notification.decode(data);
    console.log('Dawn TCP-Received');
    if (decoded.header === Notification.Type.STUDENT_RECEIVED) {
      RendererBridge.reduxDispatch(notifyChange(uploadStatus.RECEIVED));
    }
  });
  runtimeSocket = sock;
});
tcp.on('error', (err) => {
  console.error(err);
});
tcp.listen(tcpPort, () => {
  console.log('Server Bound');
});


ipcMain.on('NOTIFY_UPLOAD', (event) => {
  console.log(event);
  const message = new Notification({
    header: Notification.Type.STUDENT_SENT,
    console_output: '',
  });
  runtimeSocket.write(message.encode().toBuffer(), () => {
    console.log('Runtime Notified');
  });
  received = false;
  RendererBridge.reduxDispatch(notifyChange(uploadStatus.SENT));
  let count = 0;
  while ((!received) && count < 3) {
    runtimeSocket.write(message.encode().toBuffer(), () => {
      console.log('Runtime Notified');
    });
    count += 1;
    const timestamp = Date.now();
    while (Date.now() - timestamp < 1000) {

    }
  }
  if (!received) {
    console.error('No Confirmation');
    RendererBridge.reduxDispatch(notifyChange(uploadStatus.ERROR));
  }
});


/**
 * Serialize the data using protocol buffers.
 */
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
  console.log(`Student Code Status: ${status}`);
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

/**
 * Receives data from the renderer process and sends that data
 * (serialized by protobufs) to the robot Runtime
 */
ipcMain.on('stateUpdate', (event, data) => {
  const message = buildProto(data);
  const buffer = message.encode().toBuffer();
  console.log('Dawn UDP-Sent');
  // Send the buffer over UDP to the robot.
  client.send(buffer, clientPort, runtimeIP, (err) => {
    if (err) {
      console.error('UDP socket error on send:', err);
    }
  });
});

ipcMain.on('ipAddress', (event, data) => {
  runtimeIP = data.ipAddress;
});

/**
 * Handler to receive messages from the robot Runtime
 */
server.on('message', (msg) => {
  try {
    const data = RuntimeData.decode(msg);
    console.log('Dawn Received UDP');
    RendererBridge.reduxDispatch(infoPerMessage(data.robot_state));
    RendererBridge.reduxDispatch(updatePeripherals(data.sensor_data));
  } catch (e) {
    console.log(`Error decoding: ${e}`);
  }
});

server.on('error', (err) => {
  console.log(`Server error:\n${err.stack}`);
  server.close();
});

server.on('close', () => {
  RendererBridge.reduxDispatch(ansibleDisconnect());
  console.log('Server Closed');
});

server.bind(serverPort);
