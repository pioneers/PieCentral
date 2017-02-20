/**
 * Simulates the robot runtime for development and testing purposes.
 *
 * NOTE: FakeRuntime is NOT transpiled or bundled by webpack like most of the other JS code
 * It will be run "as is" as a child-process of the rest of the application.
 * Some experimental features that are used elsewhere in Dawn may not be available here.
 */

const dgram = require('dgram');
const ProtoBuf = require('protobufjs');

const dawnBuilder = ProtoBuf.loadProtoFile('../ansible-protos/ansible.proto');
const DawnData = dawnBuilder.build('DawnData');
const runtimeBuilder = ProtoBuf.loadProtoFile('../ansible-protos/runtime.proto');
const RuntimeData = runtimeBuilder.build('RuntimeData');

const clientPort = 1235; // send port
const serverPort = 1236; // receive port
const hostname = 'localhost';
const client = dgram.createSocket('udp4');// sender
const server = dgram.createSocket('udp4'); // receiver
const SENDRATE = 1000;
const stateEnum = {
  RUNNING: 1,
  IDLE: 0,
};
let state = stateEnum.IDLE;

/**
 * Handler to receive messages from Dawn.
 * We don't do anything besides decode it and print it out.
 */
server.on('message', (msg) => {
  // Decode and get the raw object.
  const data = DawnData.decode(msg).toRaw();
  console.log(data);
  if (data.student_code_status !== 'IDLE') {
    state = stateEnum.RUNNING;
  } else {
    state = stateEnum.IDLE;
  }
});

server.bind(serverPort, hostname);

/**
 * Returns a random number between min and max.
 */
const randomFloat = (min, max) => (((max - min) * Math.random()) + min);

/**
 * Generate fake data to send to Dawn
 */
const generateFakeData = () => [
  {
    robot_state: state,
    sensor_data: [{
      device_type: 'MOTOR_SCALAR',
      device_name: 'MS1',
      value: randomFloat(-100, 100),
      uid: 100,
    }, {
      device_type: 'MOTOR_SCALAR',
      device_name: 'MS2',
      value: randomFloat(-100, 100),
      uid: 105,
    }, {
      device_type: 'LimitSwitch',
      device_name: 'LS1',
      value: Math.round(randomFloat(0, 1)),
      uid: 101,
    }, {
      device_type: 'SENSOR_SCALAR',
      device_name: 'SS1',
      value: randomFloat(-100, 100),
      uid: 102,
    }, {
      device_type: 'SENSOR_SCALAR',
      device_name: 'SS2',
      value: randomFloat(-100, 100),
      uid: 106,
    }, {
      device_type: 'ServoControl',
      device_name: 'SC1',
      value: Math.round(randomFloat(0, 180)),
      uid: 103,
    }, {
      device_type: 'ColorSensor',
      device_name: 'CS1',
      value: Math.round(randomFloat(0, 255)),
      uid: 104,
    }],
  },
];

/**
 * Send the encoded randomly generated data to Dawn
 */
setInterval(() => {
  const fakeData = generateFakeData();
  for (const item of fakeData) {
    const udpData = new RuntimeData(item);
    client.send(Buffer.from(udpData.toArrayBuffer()), clientPort, hostname);
  }
}, SENDRATE);
