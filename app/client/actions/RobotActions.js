import AppDispatcher from '../dispatcher/AppDispatcher';
import {ActionTypes} from '../constants/Constants';
import AnsibleClient from '../utils/AnsibleClient';

var RobotActions = {
  updateMotor(id, speed) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_MOTOR,
      id: id,
      value: speed
    });
  },
  updatePeripheral(id, value) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_PERIPHERAL,
      peripheralType: ActionTypes.SENSOR_SCALAR,
      id: id,
      value: value
    });
  }
};

export default RobotActions;
