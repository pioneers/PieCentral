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
    SAVE_FILE: null,
    OPEN_FILE: null,
    CLEAR_EDITOR: null,
    UPDATE_CONSOLE: null,
    UPDATE_PERIPHERAL_NAME: null
  }),
  PeripheralTypes: keyMirror({
    MOTOR_SCALAR: null,
    SENSOR_BOOLEAN: null,
    SENSOR_SCALAR: null
  })
};
