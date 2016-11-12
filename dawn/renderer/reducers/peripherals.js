const peripherals = (state = {}, action) => {
  const nextState = Object.assign({}, state);

  switch (action.type) {
    case 'UPDATE_PERIPHERAL':
      nextState[action.peripheral.uid] = action.peripheral;
      return nextState;
    case 'PERIPHERAL_DISCONNECT':
      delete nextState[action.peripheral.uid];
      return nextState;
    default:
      return state;
  }
};

export default peripherals;
