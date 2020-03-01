import { createActions } from 'redux-actions';

export const { updateSensors } = createActions({
  UPDATE_SENSORS: ({ devices }) => ({ sensors: devices, timestamp: new Date() }),
});
