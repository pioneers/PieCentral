import keyMirror from 'keymirror';

export default {
  ActionTypes: keyMirror({
    UPDATE_MOTOR: null,
    UPDATE_PERIPHERAL: null
  }),
  PeripheralTypes: keyMirror({
    MOTOR_SCALAR: null,
    SENSOR_BOOLEAN: null,
    SENSOR_SCALAR: null
  })
};
