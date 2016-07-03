/**
 * Imitates the Robot runtime by sending fake data to the frontend.
 */

import RendererBridge from './RendererBridge';
import _ from 'lodash';

/**
 * Returns a random number between min and max.
 */
const randomFloat = (min, max) => ((max - min) * Math.random() + min);

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
];

const FakeRuntime = {
  interval: null,

  isActive() {
    return this.interval !== null;
  },

  start(delay) {
    RendererBridge.reduxDispatch({ type: 'ANSIBLE_CONNECT' });
    this.interval = setInterval(() => {
      generateFakeData().forEach((val) => {
        RendererBridge.reduxDispatch(val);
      });
    }, delay);
  },

  stop() {
    clearInterval(this.interval);
    this.interval = null;
    RendererBridge.reduxDispatch({ type: 'ANSIBLE_DISCONNECT' });
  },
};

_.bindAll(FakeRuntime, ['start', 'stop', 'isActive']);

export default FakeRuntime;
