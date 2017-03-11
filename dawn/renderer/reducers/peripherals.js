import { PeripheralTypes } from '../constants/Constants';

const initialPeripheralState = {
  peripheralList: {},
  batterySafety: false,
  batteryLevel: 0,
  runtimeVersion: '0.0.0',
};

const peripherals = (state = initialPeripheralState, action) => {
  const nextState = Object.assign({}, state);
  const nextPeripherals = nextState.peripheralList;
  switch (action.type) {
    case 'UPDATE_PERIPHERALS': {
      const keys = [];
      action.peripherals.forEach((peripheral) => {
        if (peripheral.device_type === PeripheralTypes.BatteryBuzzer) {
          if (peripheral.param_value[0].param === 'is_unsafe') {
            nextState.batterySafety = peripheral.param_value[0].bool_value;
            nextState.batteryLevel = peripheral.param_value[1].float_value;
          } else {
            nextState.batteryLevel = peripheral.param_value[0].float_value;
            nextState.batterySafety = peripheral.param_value[1].bool_value;
          }
        } else if (peripheral.uid === '-1') {
          let major = '';
          let minor = '';
          let patch = '';
          peripheral.param_value.forEach((obj) => {
            if (obj.param === 'major') {
              major = obj[obj.kind];
            } else if (obj.param === 'minor') {
              minor = obj[obj.kind];
            } else {
              patch = obj[obj.kind];
            }
          });
          nextState.runtimeVersion = `${major}.${minor}.${patch}`;
        } else {
          keys.push(peripheral.uid);
          if (peripheral.uid in nextPeripherals) {
            peripheral.device_name = nextPeripherals[peripheral.uid].device_name;
          }
          nextPeripherals[peripheral.uid] = peripheral;
        }
      });
      Object.keys(nextPeripherals).forEach((el) => {
        if (keys.indexOf(el) === -1) {
          delete nextPeripherals[el];
        }
      });
      return nextState;
    }
    case 'PERIPHERAL_DISCONNECT': {
      delete nextPeripherals[action.id];
      return nextState;
    }
    case 'PERIPHERAL_RENAME': {
      nextPeripherals[action.id].name = action.name;
      return nextState;
    }
    default: {
      return state;
    }
  }
};

export default peripherals;
