import AppDispatcher from '../dispatcher/AppDispatcher';
import Constants from '../constants/Constants';
var ActionTypes = Constants.ActionTypes;

export default {
  updateMotor(id, speed) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_MOTOR,
      id: id,
      speed: speed
    });
  }
};
