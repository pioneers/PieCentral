const gamepads = (state = {}, action) => {
  switch (action.type) {
    case 'UPDATE_GAMEPADS':
      return {
        ...state,
        gamepads: action.gamepads,
      };
    default:
      return state;
  }
};

export default gamepads;
