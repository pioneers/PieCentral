/**
 * Actions for asynchronous (non-blocking) alerts.
 */
import seedrandom from 'seedrandom';

const rng = seedrandom('alertseed');

export const addAsyncAlert = (heading, message) => ({
  type: 'ADD_ASYNC_ALERT',
  id: rng.int32(),
  heading,
  message,
});

export const removeAsyncAlert = id => ({
  type: 'REMOVE_ASYNC_ALERT',
  id,
});
