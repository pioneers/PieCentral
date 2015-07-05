import AppDispatcher from '../dispatcher/AppDispatcher';
import Constants from '../constants/Constants';
import {EventEmitter} from 'events';
import assign from 'object-assign';
var ActionTypes = Constants.ActionTypes;

// Private data.
var motors = {};

var RemoteRobotStore = assign({}, EventEmitter.prototype, {
  emitChange() {
    this.emit('change');
  },
  getMotors() {
    return motors;
  }
});

/* Handles receiving an UPDATE_MOTOR action
 */
function handleUpdateMotor(action) {
  var id = action.id;
  var speed = action.speed;
  motors[id] = {id, speed};
  RemoteRobotStore.emitChange();
}

RemoteRobotStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.type) {
    case ActionTypes.UPDATE_MOTOR:
      handleUpdateMotor(action);
      break;
  }
});

export default RemoteRobotStore;
