import { ipcRenderer } from 'electron';
import { ActionTypes } from '../constants/Constants';
import { robotState, runtimeState, defaults } from '../utils/utils';

const initialInfoState = {
  ipAddress: defaults.IPADDRESS,
  studentCodeStatus: robotState.IDLE,
  robotState: runtimeState.STUDENT_STOPPED,
  isRunningCode: false,
  connectionStatus: false,
  runtimeStatus: false,
  notificationHold: 0,
  fieldControlDirective: robotState.TELEOP,
  fieldControlActivity: false,
};

const info = (state = initialInfoState, action) => {
  switch (action.type) {
    case 'PER_MESSAGE':
      return {
        ...state,
        connectionStatus: true,
        robotState: action.robotState,
        isRunningCode: (action.robotState === runtimeState.STUDENT_RUNNING ||
        action.robotState === runtimeState.TELEOP ||
        action.robotState === runtimeState.AUTONOMOUS),
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
    case 'CODE_STATUS':
      ipcRenderer.send('studentCodeStatus', { studentCodeStatus: action.studentCodeStatus });
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
    case ActionTypes.UPDATE_ROBOT:
      return {
        ...state,
        fieldControlDirective: (action.autonomous) ? robotState.AUTONOMOUS : robotState.TELEOP,
        fieldControlActivity: action.enabled,
        // eslint-disable-next-line no-nested-ternary
        studentCodeStatus: (state.fieldControlActivity && !action.enabled)
          ? robotState.IDLE :
          (action.autonomous) ? robotState.AUTONOMOUS : robotState.TELEOP,
      };
    default:
      return state;
  }
};

export default info;
