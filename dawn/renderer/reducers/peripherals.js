import { PeripheralTypes } from '../constants/Constants';

const initialPeripheralState = {
  peripheralList: {},
  batterySafety: false,
  batteryLevel: 0,
  runtimeVersion: '0.0.0',
};

function getParams(peripheral) {
  const res = {};
  peripheral.param_value.forEach((obj) => {
    res[obj.param] = obj[obj.kind];
  });
  return res;
}

const peripherals = (state = initialPeripheralState, action) => {
  const nextState = Object.assign({}, state);
  const nextPeripherals = nextState.peripheralList;
  switch (action.type) {
    case 'UPDATE_PERIPHERALS': {
      const keys = [];
      action.peripherals.forEach((peripheral) => {
        if (peripheral.device_type === PeripheralTypes.BatteryBuzzer) {
          const batteryParams = getParams(peripheral);
          if (batteryParams.is_unsafe !== undefined) {
            nextState.batterySafety = batteryParams.is_unsafe;
          }
          if (batteryParams.v_batt !== undefined) {
            nextState.batteryLevel = batteryParams.v_batt;
          }
        } else if (peripheral.uid === '-1') {
          const version = getParams(peripheral);
          nextState.runtimeVersion = `${version.major}.${version.minor}.${version.patch}`;
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
    // Note: This is not being used since NameEdit is still broken
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
