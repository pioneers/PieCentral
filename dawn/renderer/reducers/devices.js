const devices = (state = [], action) => {
  switch (action.type) {
    case 'ADD_DEVICE':
      return [
        ...state,
      ];
    // case 'RENAME_DEVICE':
    //   return [
    //   ];
    default:
      return state;
  }
};

export default devices;
