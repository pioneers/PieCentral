import { ipcMain } from 'electron';
import ProtoBuf from 'protobufjs';
import dgram from 'dgram';
import _ from 'lodash';
import {
    ansibleConnect,
    ansibleDisconnect,
    updateStatus,
    updateRobotState,
} from '../../renderer/actions/InfoActions';
import { updatePeripheral } from '../../renderer/actions/PeripheralActions';
import RendererBridge from '../RendererBridge';

let runtimeIP = 'localhost';  // '192.168.128.22';
const clientPort = 1236; // send port
const serverPort = 1235; // receive port
const client = dgram.createSocket('udp4'); // sender
const server = dgram.createSocket('udp4'); // receiver

const dawnBuilder = ProtoBuf.loadProtoFile(`${__dirname}/ansible.proto`);
const DawnData = dawnBuilder.build('DawnData');
const StudentCodeStatus = DawnData.StudentCodeStatus;

const runtimeBuilder = ProtoBuf.loadProtoFile(`${__dirname}/runtime.proto`);
const RuntimeData = runtimeBuilder.build('RuntimeData');

/**
 * Serialize the data using protocol buffers.
 */
function buildProto(data) {
  const status = data.studentCodeStatus ?
    StudentCodeStatus.TELEOP : StudentCodeStatus.IDLE;
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
  RendererBridge.reduxDispatch(ansibleConnect());
  RendererBridge.reduxDispatch(updateStatus());
  try {
    const data = RuntimeData.decode(msg);
    RendererBridge.reduxDispatch(updateRobotState(data.robot_state));
    for (const sensor of data.sensor_data) {
      RendererBridge.reduxDispatch(updatePeripheral(sensor));
    }
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
