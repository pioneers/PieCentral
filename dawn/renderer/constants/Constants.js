import keyMirror from 'keymirror';

export const VERSION = '0.6.0';
export const PeripheralTypes = keyMirror({
  MOTOR_SCALAR: null,
  SENSOR_BOOLEAN: null,
  SENSOR_SCALAR: null,
  LimitSwitch: null,
  LineFollower: null,
  Potentiometer: null,
  Encoder: null,
  ColorSensor: null,
  MetalDetector: null,
  ExampleDevice: null,
  ServoControl: null,
  YogiBear: null,
  RFID: null,
  BatteryBuzzer: null,
  TeamFlag: null,
});
