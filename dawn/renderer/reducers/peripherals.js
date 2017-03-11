const peripherals = (state = {}, action) => {
  const nextState = Object.assign({}, state);
  switch (action.type) {
    case 'UPDATE_PERIPHERALS': {
      const keys = [];
      action.peripherals.forEach((peripheral) => {
        keys.push(peripheral.uid);
        if (peripheral.uid in nextState) {
          peripheral.device_name = nextState[peripheral.uid].device_name;
        }
        nextState[peripheral.uid] = peripheral;
      });
      Object.keys(nextState).forEach((el) => {
        if (keys.indexOf(el) === -1) {
          delete nextState[el];
        }
      });
      return nextState;
    }
    case 'PERIPHERAL_DISCONNECT': {
      delete nextState[action.id];
      return nextState;
    }
    case 'PERIPHERAL_RENAME': {
      nextState[action.id].name = action.name;
      return nextState;
    }
    default: {
      return state;
    }
  }
};

export default peripherals;
