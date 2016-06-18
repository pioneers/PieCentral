const info = (state={}, action) => {
  switch (action.type) {
    case 'ANSIBLE_CONNECT':
      return {
        ...state,
        connectionStatus: true
      };
    case 'ANSIBLE_DISCONNECT':
      return {
        ...state,
        connectionStatus: false
      };
    case 'RUNTIME_CONNECT':
      return {
        ...state,
        runtimeStatus: true
      };
    case 'RUNTIME_DISCONNECT':
      return {
        ...state,
        runtimeStatus: false
      };
    case 'UPDATE_BATTERY':
      return {
        ...state,
        batteryLevel: action.battery.value
      };
    case 'UPDATE_STATUS':
      return {
        ...state,
        isRunningCode: (action.status.value === 1)
      };
    case 'runtime_version':
      return {
        ...state,
        runtimeVersion: {
          version: action.version,
          headhash: action.headhash,
          modified: action.modified
        }
      };
    default:
      return state;
  }
};

export default info;
