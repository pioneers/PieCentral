import AppDispatcher from '../dispatcher/AppDispatcher';
import {EventEmitter} from 'events';
import { ActionTypes } from '../constants/Constants';
import assign from 'object-assign';
import _ from 'lodash';
import Immutable from 'immutable';

let _robotInfo = {
  consoleData: Immutable.List(),
  connectionStatus: false,
  runtimeStatus: true, // Are we receiving data from runtime?
  isRunningCode: false, // Is runtime executing code?
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
  getRuntimeStatus() {
    return _robotInfo.runtimeStatus;
  },
  getIsRunningCode() {
    return _robotInfo.isRunningCode;
  },
  getBatteryLevel() {
    return _robotInfo.batteryLevel;
  }
});

// Here, "status" refers to whether the robot is running code.
function handleUpdateStatus(action) {
  _robotInfo.isRunningCode = (action.status.value == 1);
  RobotInfoStore.emitChange();
}

function handleUpdateBattery(action){
  _robotInfo.batteryLevel = action.battery.value;
  RobotInfoStore.emitChange();
}

/**
 * Dispatch the 'StopCheck' action every second. handleStopCheck
 * uses this to determine runtimeStatus.
 */

var previousActionType = null;
setInterval(() => {
  AppDispatcher.dispatch({
    type: 'StopCheck',
    content: {}
  });
}, 1000);

/* Determines connection status. If we receive a StopCheck action,
 * and the previous action was also a StopCheck, then we have received
 * no status updates in the past second and we are disconnected.
 */
function handleStopCheck(action) {
  var old = _robotInfo.runtimeStatus;
  if (previousActionType === 'StopCheck') {
    _robotInfo.runtimeStatus = false;
  } else {
    _robotInfo.runtimeStatus = true;
  }
  if (old !== _robotInfo.runtimeStatus) {
    RobotInfoStore.emitChange();
  }
}

function handleConsoleUpdate(action) {
  _robotInfo.consoleData = _robotInfo.consoleData.push(action.console_output.value);
  // keep the length of console output less than 20 lines
  if (_robotInfo.consoleData.size > 20)
    _robotInfo.consoleData = _robotInfo.consoleData.shift();
  RobotInfoStore.emitChange();
}

function handleClearConsole(action) {
  _robotInfo.consoleData = _robotInfo.consoleData.clear();
  RobotInfoStore.emitChange();
}

function handleUpdateConnection(action) {
  _robotInfo.connectionStatus = action.payload;
  RobotInfoStore.emitChange();
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
    case ActionTypes.UPDATE_CONNECTION:
      handleUpdateConnection(action);
      break;
    case 'StopCheck':
      handleStopCheck(action);
      previousActionType = action.type;
      break;
  }
});

export default RobotInfoStore;
