/**
 * Actions for asynchronous (non-blocking) alerts.
 */

let nextAsyncAlertId = 0;
export const addAsyncAlert = (heading, message) => {
  return {
    type: 'ADD_ASYNC_ALERT',
    id: nextAsyncAlertId++,
    heading: heading,
    message: message
  };
};

export const removeAsyncAlert = (id) => {
  return {
    type: 'REMOVE_ASYNC_ALERT',
    id: id
  };
};
