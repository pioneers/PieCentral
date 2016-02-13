import AppDispatcher from '../dispatcher/AppDispatcher';
import { ActionTypes } from '../constants/Constants';

let AlertActions = {
  addAlert(heading, message) {
    AppDispatcher.dispatch({
      type: ActionTypes.ADD_ALERT,
      payload: {
        heading: heading,
        message: message
      }
    });
  },
  removeAlert(alert) {
    AppDispatcher.dispatch({
      type: ActionTypes.REMOVE_ALERT,
      payload: alert
    });
  }
};

export default AlertActions;
