import { ipcRenderer } from 'electron';
import { robotState } from '../utils/utils';

const initialInfoState = {
  ipAddress: '192.168.7.2',
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
        isRunningCode: (action.robotState === robotState.TELEOP ||
        action.robotState === robotState.AUTONOMOUS),
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
        studentCodeStatus: robotState.IDLE,
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
