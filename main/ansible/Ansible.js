import { ipcMain } from 'electron';
import ProtoBuf from 'protobufjs';
import dgram from 'dgram';
import _ from 'lodash';

const hostname = 'localhost';
const clientPort = '12345'; // send port
const serverPort = '12346'; // receive port
const client = dgram.createSocket('udp4'); // sender
const server = dgram.createSocket('udp4'); // receiver

const dawnBuilder = ProtoBuf.loadProtoFile('./main/ansible/ansible-protos/ansible.proto');
const DawnData = dawnBuilder.build('DawnData');
const StudentCodeStatus = DawnData.StudentCodeStatus;

const runtimeBuilder = ProtoBuf.loadProtoFile('./main/ansible/ansible-protos/runtime_proto.proto');
const RuntimeData = runtimeBuilder.build('RuntimeData');

/**
 * Serialize the data using protocol buffers.
 */
function buildProto(data) {
  const status = data.stuentCodeStatus ?
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
  client.send(buffer, clientPort, hostname, (err) => {
    if (err) {
      console.error('UDP socket error on send:', err);
    }
  });
});

/**
 * Handler to receive messages from the robot Runtime
 */
server.on('message', (msg) => {
  const data = RuntimeData.decode(msg).toRaw();
  console.log(`Dawn received: ${JSON.stringify(data)}\n`);
});

server.bind(serverPort, hostname);
