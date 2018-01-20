/*
 * Fake Runtime is not handled by webpack like most of the other JS code but instead
 * will be run "as is" as a child-process of the rest of the application.
 * See DebugMenu.js for handling FakeRuntime within Dawn
 */

const dgram = require('dgram');
const net = require('net');
const protobuf = require('protobufjs');

const DawnData = (new protobuf.Root()).loadSync('../ansible-protos/ansible.proto', { keepCase: true }).lookupType('DawnData');
const RuntimeData = (new protobuf.Root()).loadSync('../ansible-protos/runtime.proto', { keepCase: true }).lookupType('RuntimeData');
const Notification = (new protobuf.Root()).loadSync('../ansible-protos/notification.proto', { keepCase: true }).lookupType('Notification');

const SENDPORT = 1235;
const LISTENPORT = 1236;
const MSGINTERVAL = 1000; // in ms
const randomFloat = (min, max) => (((max - min) * Math.random()) + min);


class FakeRuntime {
  constructor() {
    this.sendSocket = dgram.createSocket({ type: 'udp4', reuseAddr: true });

    this.listenSocket = dgram.createSocket({ type: 'udp4', reuseAddr: true });
    this.fakeState = RuntimeData.State.STUDENT_STOPPED;
    this.listenSocket.on('message', (msg) => {
      const data = DawnData.decode(msg);
      switch (data.student_code_status) {
        case DawnData.StudentCodeStatus.TELEOP:
          if (this.fakeState !== RuntimeData.State.TELEOP) {
            console.log('Fake Runtime in Teleop');
            this.fakeState = RuntimeData.State.TELEOP;
          }
          break;
        case DawnData.StudentCodeStatus.ESTOP:
          if (this.fakeState !== RuntimeData.State.ESTOP) {
            console.log('Fake Runtime Estopped');
            this.fakeState = RuntimeData.State.ESTOP;
          }
          break;
        case DawnData.StudentCodeStatus.AUTONOMOUS:
          if (this.fakeState !== RuntimeData.State.AUTO) {
            console.log('Fake Runtime in Autonomous');
            this.fakeState = RuntimeData.State.AUTO;
          }
          break;
        default:
          if (this.fakeState !== RuntimeData.State.STUDENT_STOPPED) {
            console.log('Fake Runtime in IDLE');
          }
          this.fakeState = RuntimeData.State.STUDENT_STOPPED;
      }
    });
    this.listenSocket.bind(LISTENPORT);


    this.tcpSocket = new net.Socket();
    this.tcpSocket.connect({ host: '127.0.0.1', port: 1234 }, () => {
      console.log('Fake Runtime TCP Up');
    });
    this.tcpSocket.on('close', () => {
      console.log('Fake Runtime TCP Down');
    });
    setInterval(this.onInterval, MSGINTERVAL);

    this.generateFakeData = this.generateFakeData.bind(this);
    this.onInterval = this.onInterval.bind(this);
  }

  generateFakeData() {
    return {
      robot_state: this.fakeState,
      sensor_data: [{
        device_type: 'MOTOR_SCALAR',
        device_name: 'MS1',
        param_value: [{
          param: 'Val',
          float_value: randomFloat(-100, 100),
        }],
        uid: '100',
      }, {
        device_type: 'MOTOR_SCALAR',
        device_name: 'MS2',
        param_value: [{
          param: 'Val',
          float_value: randomFloat(-100, 100),
        }],
        uid: '101',
      }, {
        device_type: 'LimitSwitch',
        device_name: 'LS1',
        param_value: [{
          param: 'Val',
          int_value: Math.round(randomFloat(0, 1)),
        }],
        uid: '102',
      }, {
        device_type: 'SENSOR_SCALAR',
        device_name: 'SS1',
        param_value: [{
          param: 'Val',
          float_value: randomFloat(-100, 100),
        }],
        uid: '103',
      }, {
        device_type: 'SENSOR_SCALAR',
        device_name: 'SS2',
        param_value: [{
          param: 'Val',
          float_value: randomFloat(-100, 100),
        }],
        uid: '104',
      }, {
        device_type: 'ServoControl',
        device_name: 'SC1',
        param_value: [{
          param: 'Val',
          int_value: Math.round(randomFloat(0, 180)),
        }],
        uid: '105',
      }],
    };
  }


  onInterval() {
    const udpData = RuntimeData.create(this.generateFakeData());
    this.sendSocket.send(RuntimeData.encode(udpData).finish(), SENDPORT, 'localhost');
    if (this.fakeState !== RuntimeData.State.ESTOP
      && this.fakeState !== RuntimeData.State.STUDENT_STOPPED) {
      const tcpData = Notification.create({
        header: Notification.Type.CONSOLE_LOGGING,
        console_output: `${randomFloat(-100, 100)}\n`,
      });
      this.tcpSocket.write(Notification.encode(tcpData).finish());
    }
  }
}

FakeRuntime();
