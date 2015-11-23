import keyMirror from 'keymirror';

module.exports = {
  VERSION: '0.4.0',
  ActionTypes: keyMirror({
    UPDATE_BATTERY:null,
    UPDATE_GAMEPADS: null,
    UPDATE_EDITOR: null,
    UPDATE_FILENAMES: null,
    UPDATE_FILENAME: null,
    UPDATE_MOTOR: null,
    UPDATE_PERIPHERAL: null,
    UPDATE_STATUS: null,
    SEND_CODE: null,
    GET_CODE: null,
    UPDATE_CONSOLE: null
  }),
  PeripheralTypes: keyMirror({
    MOTOR_SCALAR: null,
    SENSOR_BOOLEAN: null,
    SENSOR_SCALAR: null
  })
};
