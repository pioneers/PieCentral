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
  notificationHold: 0,
};

const info = (state = initialInfoState, action) => {
  switch (action.type) {
    case 'PER_MESSAGE':
      return {
        ...state,
        connectionStatus: true,
        robotState: action.robotState,
        isRunningCode: (action.robotState === 1 ||
        action.robotState === 3 || action.robotState === 4),
      };
    case 'ANSIBLE_DISCONNECT':
      return {
        ...state,
        connectionStatus: false,
      };
    case 'NOTIFICATION_CHANGE':
      return {
        ...state,
        notificationHold: action.notificationHold,
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
    default:
      return state;
  }
};

export default info;
