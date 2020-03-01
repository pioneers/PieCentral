import { createActions } from 'redux-actions';

export const { addHeartbeat, setStatus } = createActions({
  ADD_HEARTBEAT: () => new Date(),
  SET_STATUS: status => ({ status }),
});
