const DEFAULT = [
  {type: 'LineFollower', uid: '103949402920394'},
  {type: 'BatteryBuzzer', alias: 'my_batt', uid: '103949402920394'},
  {type: 'PolarBear', uid: '103949402920394'},
  {type: 'PolarBear', uid: '103949402920394'},
  {type: 'PolarBear', uid: '103949402920394'},
]

const devices = (state = DEFAULT, action) => {
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
