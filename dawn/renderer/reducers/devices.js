import _ from 'lodash';

const DEFAULT_DEVICES = {
  sensors: {},
  gamepads: {},
  order: [],
  maxPoints: 100,
};

const devices = (state = DEFAULT_DEVICES, action) => {
  switch (action.type) {
    case 'UPDATE_SENSORS':
      let sensors = _.mapValues(action.payload.sensors, (sensor, uid) => {
        let existingSensor = state.sensors[uid], params;
        // params = {}; // FIXME
        if (existingSensor) {
          params = _.mapValues(sensor.params, (value, paramName) =>
            [...existingSensor.params[paramName], value].slice(-state.maxPoints));
        } else {
          console.log('NEW');
          params = _.mapValues(sensor.params, (value, paramName) => [value]);
        }
        console.log(state);
        return { ...sensor, params };
      });
      return { ...state, sensors };
    default:
      return state;
  }
};

export default devices;
