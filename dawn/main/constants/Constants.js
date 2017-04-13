import keyMirror from 'keymirror';

module.exports = {
  VERSION: '0.4.0',
  ActionTypes: keyMirror({
    UPDATE_BATTERY:null,
    UPDATE_GAMEPADS: null,
    UPDATE_EDITOR: null,
    UPDATE_FILENAMES: null,
    UPDATE_FILENAME: null,
    UPDATE_PERIPHERAL: null,
    UPDATE_STATUS: null,
    UPDATE_CONNECTION: null,
    SAVE_FILE: null,
    OPEN_FILE: null,
    CLEAR_EDITOR: null,
    UPDATE_CONSOLE: null,
    UPDATE_TIMER: null,
    UPDATE_HEART: null,
    UPDATE_ROBOT: null,
    UPDATE_MATCH: null,
    UPDATE_SCORE: null,
    ADD_ALERT: null,
    REMOVE_ALERT: null,
    CLEAR_CONSOLE: null,
    runtime_version: null
  }),
  PeripheralTypes: keyMirror({
    MOTOR_SCALAR: null,
    SENSOR_BOOLEAN: null,
    SENSOR_SCALAR: null,
    LimitSwitch: null,
    LineFollower: null,
    Potentiometer: null,
    Encoder: null,
    ColorSensor: null,
    MetalDetector: null,
    ExampleDevice: null
  })
};
