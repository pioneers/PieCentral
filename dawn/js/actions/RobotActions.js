import AppDispatcher from '../dispatcher/AppDispatcher';
import {ActionTypes} from '../constants/Constants';

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
  },
  clearConsole() {
    AppDispatcher.dispatch({
      type: ActionTypes.CLEAR_CONSOLE,
    });
  },
  updatePeripheralName(id, newName) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_PERIPHERAL_NAME,
      id: id,
      newName: newName
    });
  }
};

export default RobotActions;
