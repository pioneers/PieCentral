import keyMirror from 'keymirror';

export const REG_VERSION = '0.7.0';
export const FC_VERSION = 'FC-0.3.0';
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

export const ActionTypes = keyMirror({
  FIELD_CONTROL: null,
  UPDATE_BATTERY: null,
  UPDATE_GAMEPADS: null,
  UPDATE_EDITOR: null,
  UPDATE_FILENAMES: null,
  UPDATE_FILENAME: null,
  UPDATE_PERIPHERAL: null,
  UPDATE_STATUS: null,
  UPDATE_CONNECTION: null,
  UPDATE_FC_CONFIG: null,
  SAVE_FILE: null,
  OPEN_FILE: null,
  CLEAR_EDITOR: null,
  UPDATE_CONSOLE: null,
  UPDATE_TIMER: null,
  UPDATE_HEART: null,
  UPDATE_ROBOT: null,
  UPDATE_MATCH: null,
  ADD_ALERT: null,
  REMOVE_ALERT: null,
  CLEAR_CONSOLE: null,
  runtime_version: null,
});
