const peripherals = (state = {}, action) => {
  const nextState = Object.assign({}, state);
  switch (action.type) {
    case 'UPDATE_PERIPHERALS': {
      const keys = [];
      action.peripherals.forEach((peripheral) => {
        const key = String(peripheral.uid.high) + String(peripheral.uid.low);
        keys.push(key);
        if (key in nextState) {
          peripheral.device_name = nextState[key].device_name;
        }
        nextState[key] = peripheral;
      });
      Object.keys(nextState).forEach((el) => {
        if (keys.indexOf(el) === -1) {
          console.log(keys);
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
      nextState[action.id] = state[action.id];
      console.log(nextState[action.id]);
      nextState[action.id].name = action.name;
      console.log(nextState[action.id]);
      return nextState;
    }
    default: {
      return state;
    }
  }
};

export default peripherals;
