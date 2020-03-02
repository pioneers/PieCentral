import { createActions } from 'redux-actions';
import { ConnectionStatus } from '../constants/Constants';

export const Mode = {
  IDLE: 'IDLE',
  AUTO: 'AUTO',
  TELEOP: 'TELEOP',
  ESTOP: 'ESTOP',
};

export const Alliance = {
  BLUE: 'BLUE',
  GOLD: 'GOLD',
};

export const { addHeartbeat, setMatch, setConnectionStatus } = createActions({
  ADD_HEARTBEAT: () => new Date(),
  SET_MATCH: (mode = null, alliance = null) => ({ mode, alliance }),
  SET_CONNECTION_STATUS: status => ({ status }),
});
