import { ipcRenderer } from 'electron';

const initialInfoState = {
  ipAddress: '192.168.7.2',
  port: 22,
  username: 'ubuntu',
  password: 'temppwd',
  studentCodeStatus: 0,
  robotState: 2,
  isRunningCode: false,
  connectionStatus: false,
  runtimeStatus: false,
};

const info = (state = initialInfoState, action) => {
  switch (action.type) {
    case 'ANSIBLE_CONNECT':
      return {
        ...state,
        connectionStatus: true,
      };
    case 'ANSIBLE_DISCONNECT':
      return {
        ...state,
        connectionStatus: false,
      };
    case 'RUNTIME_CONNECT':
      return {
        ...state,
        runtimeStatus: true,
      };
    case 'RUNTIME_DISCONNECT':
      return {
        ...state,
        runtimeStatus: false,
      };
    case 'UPDATE_BATTERY':
      return {
        ...state,
        batteryLevel: action.battery.value,
      };
    case 'UPDATE_STATUS':
      return {
        ...state,
      };
    case 'CODE_STATUS':
      return {
        ...state,
        studentCodeStatus: action.studentCodeStatus,
      };
    case 'IP_CHANGE':
      ipcRenderer.send('ipAddress', { ipAddress: action.ipAddress });
      return {
        ...state,
        ipAddress: action.ipAddress,
      };
    case 'ROBOT_STATE':
      return {
        ...state,
        robotState: action.robotState,
        isRunningCode: (action.robotState === 1 ||
        action.robotState === 3 || action.robotState === 4),
      };
    default:
      return state;
  }
};

export default info;
