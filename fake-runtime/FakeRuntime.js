/**
 * Simulates the robot runtime for development and testing purposes.
 *
 * NOTE: FakeRuntime is NOT transpiled or bundled by webpack like most of the other JS code
 * It will be run "as is" as a child-process of the rest of the application.
 * Some experimental features that are used elsewhere in Dawn may not be available here.
 */

const dgram = require('dgram');
const ProtoBuf = require('protobufjs');
const _ = require('lodash');

const builder = ProtoBuf.loadProtoFile('./main/ansible/ansible.proto');
const AnsibleMain = builder.build('main');
const DawnData = AnsibleMain.DawnData;

const clientPort = '12346'; // send port
const serverPort = '12345'; // receive port
const hostname = 'localhost';
const client = dgram.createSocket('udp4');// sender
const server = dgram.createSocket('udp4'); // receiver

/**
 * Handler to receive messages from Dawn.
 * We don't do anything besides decode it and print it out.
 */
server.on('message', (msg, rinfo) => {
  // Decode and get the raw object.
  const data = DawnData.decode(msg).toRaw();
  console.log(`FakeRuntime received: ${JSON.stringify(data)}\n`);
});

server.bind(serverPort, hostname);

/**
 * Returns a random number between min and max.
 */
const randomFloat = (min, max) => ((max - min) * Math.random() + min);

/**
 * Generate fake data to send to Dawn
 */
const generateFakeData = () => [
  {
    type: 'UPDATE_STATUS',
    status: { value: 0 },
  },
  {
    type: 'UPDATE_PERIPHERAL',
    peripheral: {
      name: 'Motor 1',
      peripheralType: 'MOTOR_SCALAR',
      value: randomFloat(-100, 100),
      id: '1',
    },
  },
  {
    type: 'UPDATE_PERIPHERAL',
    peripheral: {
      name: 'Limit Switch 1',
      peripheralType: 'LimitSwitch',
      value: Math.round(randomFloat(0, 1)),
      id: '2',
    },
  },
  {
    type: 'UPDATE_PERIPHERAL',
    peripheral: {
      name: 'Scalar Sensor 1',
      peripheralType: 'SENSOR_SCALAR',
      value: randomFloat(-100, 100),
      id: '3',
    },
  },
  {
    type: 'UPDATE_PERIPHERAL',
    peripheral: {
      name: 'Servo 1',
      peripheralType: 'ServoControl',
      value: Math.round(randomFloat(0, 180)),
      id: '4',
    },
  },
  {
    type: 'UPDATE_PERIPHERAL',
    peripheral: {
      name: 'Color Sensor 1',
      peripheralType: 'ColorSensor',
      value: [
        Math.round(randomFloat(0, 255)),
        Math.round(randomFloat(0, 255)),
        Math.round(randomFloat(0, 255)),
        Math.round(randomFloat(0, 360)),
        Math.round(randomFloat(0, 360)),
      ],
      id: '5',
    },
  },
  {
    type: 'UPDATE_CONSOLE',
    value: 'Some print statement\n',
  },
];

/**
 * Send the encoded randomly generated data to Dawn
 */
setInterval(() => {
  const fakeData = generateFakeData();
  // Don't know what Runtime protobufs look like so
  // we are encoding with JSON for right now.
  const encodedData = JSON.stringify(fakeData);
  client.send(encodedData, clientPort, hostname);
}, 500);
