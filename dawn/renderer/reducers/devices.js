import _ from 'lodash';

const DEFAULT_DEVICES = {
  sensors: [],
  gamepads: [],
  maxPoints: 100,
};

const devices = (state = DEFAULT_DEVICES, action) => {
  switch (action.type) {
    case 'UPDATE_SENSORS':
      let existingUIDs = [];
      let sensors = _.compact(_.map(state.sensors, sensor => {
        let update = action.payload.sensors[sensor.uid];
        if (update) {
          existingUIDs.push(sensor.uid);
          return {
            ...sensor,
            params: _.mapValues(sensor.params, (trajectory, name) =>
              _.takeRight([...trajectory, update.params[name]], state.maxPoints))
          };
        }
      }));

      let newUIDs = _.difference(_.keys(action.payload.sensors), existingUIDs);
      console.log(newUIDs);
      // sensors = sensors.concat();

      // let newSensors = _.keys(action.payload.sensors).filter(
      //   uid => !state.sensors.some(sensor => sensor.uid === uid));
      // newSensors = newSensors.map(uid => ({
      //   uid,
      //   ...action.payload.sensors[uid],
      //   params: _.mapKeys(update.params) }));
      // let sensors = [...state.sensors, newSensors];

      // sensors = sensors.map(sensor => {
      //   let update = action.payload.sensors;
      //   if (update) {
      //     return {
      //       ...sensor,
      //       params: _.mapValues(update.params, (value, name) => [...sensor.params[name], value]);
      //     };
      //   }
      // });
      // console.log(sensors, state.sensors);
      return { ...state, sensors };
    default:
      return state;
  }
};

export default devices;
