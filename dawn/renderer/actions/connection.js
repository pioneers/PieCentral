import { createActions } from 'redux-actions';
import { ConnectionStatus } from '../constants/Constants';

export const { addHeartbeat, setStatus, disconnect } = createActions({
  ADD_HEARTBEAT: () => new Date(),
  SET_STATUS: status => ({ status }),
  DISCONNECT: status => null,
});
