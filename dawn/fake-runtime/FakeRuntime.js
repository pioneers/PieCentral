/*
 * Fake Runtime is not handled by webpack like most of the other JS code but instead
 * will be run "as is" as a child-process of the rest of the application.
 * See DebugMenu.js for handling FakeRuntime within Dawn
 */

const dgram = require('dgram');
const ProtoBuf = require('protobufjs');

const dawnBuilder = ProtoBuf.loadProtoFile('../ansible-protos/ansible.proto');
const DawnData = dawnBuilder.build('DawnData');
const runtimeBuilder = ProtoBuf.loadProtoFile('../ansible-protos/runtime.proto');
const RuntimeData = runtimeBuilder.build('RuntimeData');

const sendPort = 1235;
const listenPort = 1236;
const sendSocket = dgram.createSocket({ type: 'udp4', reuseAddr: true });
const listenSocket = dgram.createSocket({ type: 'udp4', reuseAddr: true });
const interval = 1000; // in ms

const robotState = {
  IDLE: 0,
  RUNNING: 1,
  ESTOP: 5,
};
let state = robotState.IDLE;

listenSocket.on('message', (msg) => {
  const data = DawnData.decode(msg);
  switch (data.student_code_status) {
    case 'IDLE':
      state = robotState.IDLE;
      break;
    case 'ESTOP':
      state = robotState.ESTOP;
      break;
    default:
      state = robotState.RUNNING;
  }
});

listenSocket.bind(listenPort);

const randomFloat = (min, max) => (((max - min) * Math.random()) + min);

const generateFakeData = () => (
  {
    robot_state: state,
    sensor_data: [{
      device_type: 'MOTOR_SCALAR',
      device_name: 'MS1',
      param_value: {
        param: 'Val',
        float_value: randomFloat(-100, 100),
      },
      uid: 100,
    }, {
      device_type: 'MOTOR_SCALAR',
      device_name: 'MS2',
      param_value: {
        param: 'Val',
        float_value: randomFloat(-100, 100),
      },
      uid: 101,
    }, {
      device_type: 'LimitSwitch',
      device_name: 'LS1',
      param_value: {
        param: 'Val',
        int_value: Math.round(randomFloat(0, 1)),
      },
      uid: 102,
    }, {
      device_type: 'SENSOR_SCALAR',
      device_name: 'SS1',
      param_value: {
        param: 'Val',
        float_value: randomFloat(-100, 100),
      },
      uid: 103,
    }, {
      device_type: 'SENSOR_SCALAR',
      device_name: 'SS2',
      param_value: {
        param: 'Val',
        float_value: randomFloat(-100, 100),
      },
      uid: 104,
    }, {
      device_type: 'ServoControl',
      device_name: 'SC1',
      param_value: {
        param: 'Val',
        int_value: Math.round(randomFloat(0, 180)),
      },
      uid: 105,
    }, {
      device_type: 'ColorSensor',
      device_name: 'CS1',
      param_value: [{
        param: 'Val',
        float_value: randomFloat(0, 255),
      }, {
        param: 'Val2',
        float_value: randomFloat(0, 255),
      }],
      uid: 106,
    }],
  });

setInterval(() => {
  const udpData = new RuntimeData(generateFakeData());
  sendSocket.send(Buffer.from(udpData.toArrayBuffer()), sendPort, 'localhost');
}, interval);
