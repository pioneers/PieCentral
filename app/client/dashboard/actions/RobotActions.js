import AppDispatcher from '../../dispatcher/AppDispatcher';
import DashboardConstants from '../constants/DashboardConstants';
var ActionTypes = DashboardConstants.ActionTypes;

export default {
  updateMotor(id, speed) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_MOTOR,
      id: id,
      value: speed
    });
  }
};
