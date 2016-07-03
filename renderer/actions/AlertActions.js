/**
 * Actions for asynchronous (non-blocking) alerts.
 */

let nextAsyncAlertId = 0;
export const addAsyncAlert = (heading, message) => ({
  type: 'ADD_ASYNC_ALERT',
  id: nextAsyncAlertId++,
  heading,
  message,
});

export const removeAsyncAlert = (id) => ({
  type: 'REMOVE_ASYNC_ALERT',
  id,
});
