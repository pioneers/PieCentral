/**
 * Stores data sourced from a physical remote robot.
 * Includes motor and sensor data.
 */
import AppDispatcher from '../dispatcher/AppDispatcher';
import {ActionTypes, PeripheralTypes} from '../constants/Constants';
import {EventEmitter} from 'events';
import assign from 'object-assign';
import _ from 'lodash';

// Private data.
var motors = {};
var peripherals = {};
var robotStatus = false;
var batteryLevel = 0;
var connectionStatus = true;
var consoleData = [];

var RemoteRobotStore = assign({}, EventEmitter.prototype, {
  emitChange() {
    this.emit('change');
  },
  getMotors() {
    return _.toArray(motors);
  },
  getPeripherals() {
    return _.toArray(peripherals); // not that efficient, rewrite if bottleneck.
  },
  getRobotStatus() {
    return robotStatus;
  },
  getBatteryLevel() {
    return batteryLevel;
  },
  getConnectionStatus() {
    return connectionStatus;
  },
  getConsoleData() {
    return consoleData;
  }
});

/**
 * Remove the motor from the motors list. Helper for handleUpdateMotor.
 */
function reapMotor(id) {
  motors[id].disconnected = true;
  motors[id].reaper = setTimeout(() => {
    delete motors[id];
    RemoteRobotStore.emitChange();
  }, 3000);
  RemoteRobotStore.emitChange();
}

/**
 * Handles receiving an UPDATE_MOTOR action. */
function handleUpdateMotor(action) {
  // Get the motor from the motors dictionary.
  var motor = motors[action.id];

  // Check if our motor exists and has a reaper.
  // If so, stop the reaper.
  // If not, make a new empty object and call that the motor.
  if (motor != null && motor.reaper != null) {
    clearTimeout(motor.reaper);
  } else {
    motor = {id: action.id, peripheralType: PeripheralTypes.MOTOR_SCALAR};
    motors[action.id] = motor;
  }

  // Motor is not disconnected.
  motor.disconnected = false;

  // Assign properties from the action.
  motor.value = action.value;

  // Assign a new reaper, which will remove this motor if
  // no updates are received after some number of milliseconds.
  motor.reaper = setTimeout(reapMotor, 500, action.id);
  // Notify listeners that the motors have been updated.
  RemoteRobotStore.emitChange();
}

/**
 * Handles receiving an UPDATE_PERIPHERAL action.
 */
function handleUpdatePeripheral(action) {
  var peripheral = action.peripheral;
  peripherals[peripheral.id] = peripheral;
  RemoteRobotStore.emitChange();
}

function handleUpdateStatus(action) {
  robotStatus = (action.status.value == 1);
  RemoteRobotStore.emitChange();
}

function handleUpdateBattery(action){
  batteryLevel = action.battery.value;
  RemoteRobotStore.emitChange();
}

/**
 * Hacking more.
 */

var previousActionType = null;
if (process.browser) {
  setInterval(() => {
    AppDispatcher.dispatch({
      type: 'StopCheck',
      content: {}
    });
  }, 1000);
}

function handleStopCheck(action) {
  var old = connectionStatus;
  if (previousActionType === 'StopCheck') {
    connectionStatus = false;
  } else {
    connectionStatus = true;
  }
  if (old !== connectionStatus) {
    RemoteRobotStore.emitChange();
  }
}

function handleConsoleUpdate(action) {
  consoleData.push(action.console_output.value);
  // keep the length of console output less than 20 lines
  if (consoleData.length > 20)
    consoleData.shift();
}

RemoteRobotStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.type) {
    case ActionTypes.UPDATE_MOTOR:
      handleUpdateMotor(action);
      previousActionType = action.type;
      break;
    case ActionTypes.UPDATE_PERIPHERAL:
      handleUpdatePeripheral(action);
      previousActionType = action.type;
      break;
    case ActionTypes.UPDATE_STATUS:
      handleUpdateStatus(action);
      previousActionType = action.type;
      break;
    case ActionTypes.UPDATE_BATTERY:
      handleUpdateBattery(action);
      previousActionType = action.type;
      break;
    case ActionTypes.UPDATE_CONSOLE:
      handleConsoleUpdate(action);
      previousActionType = action.type;
      break;
    case 'StopCheck':
      handleStopCheck(action);
      previousActionType = action.type;
      break;
  }
});

export default RemoteRobotStore;
