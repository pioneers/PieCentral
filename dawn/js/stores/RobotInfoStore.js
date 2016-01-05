import AppDispatcher from '../dispatcher/AppDispatcher';
import {EventEmitter} from 'events';
import { ActionTypes } from '../constants/Constants';
import assign from 'object-assign';
import _ from 'lodash';

let _robotInfo = {
  consoleData: '',
  connectionStatus: true,
  isRunningCode: false,
  batteryLevel: 0
};

let RobotInfoStore = assign({}, EventEmitter.prototype, {
  emitChange() {
    this.emit('change');
  },
  getConsoleData() {
    return _robotInfo.consoleData;
  },
  getConnectionStatus() {
    return _robotInfo.connectionStatus;
  },
  getIsRunningCode() {
    return _robotInfo.isRunningCode;
  },
  getBatteryLevel() {
    return _robotInfo.batteryLevel;
  }
});

function handleUpdateStatus(action) {
  _robotInfo.robotStatus = (action.status.value == 1);
  RobotInfoStore.emitChange();
}

function handleUpdateBattery(action){
  _robotInfo.batteryLevel = action.battery.value;
  RobotInfoStore.emitChange();
}

/**
 * Hacking more.
 */

var previousActionType = null;
setInterval(() => {
  AppDispatcher.dispatch({
    type: 'StopCheck',
    content: {}
  });
}, 1000);

function handleStopCheck(action) {
  var old = _robotInfo.connectionStatus;
  if (previousActionType === 'StopCheck') {
    _robotInfo.connectionStatus = false;
  } else {
    _robotInfo.connectionStatus = true;
  }
  if (old !== _robotInfo.connectionStatus) {
    RobotInfoStore.emitChange();
  }
}

function handleConsoleUpdate(action) {
  consoleData.push(action.console_output.value);
  // keep the length of console output less than 20 lines
  if (consoleData.length > 20)
    consoleData.shift();
}

function handleClearConsole(action) {
  consoleData.length = 0;
}

RobotInfoStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.type) {
    case ActionTypes.UPDATE_STATUS:
      handleUpdateStatus(action);
      previousActionType = action.type;
      break;
    case ActionTypes.UPDATE_BATTERY:
      handleUpdateBattery(action);
      break;
    case ActionTypes.UPDATE_CONSOLE:
      handleConsoleUpdate(action);
      break;
    case ActionTypes.CLEAR_CONSOLE:
      handleClearConsole(action);
      break;
    case 'StopCheck':
      handleStopCheck(action);
      previousActionType = action.type;
      break;
  }
});

export default RobotInfoStore;
