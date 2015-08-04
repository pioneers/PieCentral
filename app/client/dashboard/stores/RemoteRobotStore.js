/**
 * Stores data sourced from a physical remote robot.
 * Includes motor and sensor data.
 */
import AppDispatcher from '../../dispatcher/AppDispatcher';
import DashboardConstants from '../constants/DashboardConstants';
import {EventEmitter} from 'events';
import assign from 'object-assign';
import _ from 'lodash';
var ActionTypes = DashboardConstants.ActionTypes;

// Private data.
var motors = {};
var peripherals = {};

var RemoteRobotStore = assign({}, EventEmitter.prototype, {
  emitChange() {
    this.emit('change');
  },
  getMotors() {
    return _.toArray(motors);
  },
  getPeripherals() {
    return _.toArray(peripherals); // not that efficient, rewrite if bottleneck.
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
    motor = {id: action.id, peripheralType: DashboardConstants.PeripheralTypes.MOTOR_SCALAR};
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

RemoteRobotStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.type) {
    case ActionTypes.UPDATE_MOTOR:
      handleUpdateMotor(action);
      break;
    case ActionTypes.UPDATE_PERIPHERAL:
      handleUpdatePeripheral(action);
      break;
  }
});

export default RemoteRobotStore;
