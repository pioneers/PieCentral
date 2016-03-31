/**
 * Stores data sourced from a physical remote robot.
 * Includes motor and sensor data.
 */
import AppDispatcher from '../dispatcher/AppDispatcher';
import {Map} from 'immutable';
import {ActionTypes, PeripheralTypes} from '../constants/Constants';
import {EventEmitter} from 'events';
import assign from 'object-assign';
import _ from 'lodash';

// Private data.
let _peripherals = {};

let RobotPeripheralStore = assign({}, EventEmitter.prototype, {
  emitChange() {
    this.emit('change');
  },
  getPeripherals() {
    return _.toArray(_peripherals);
  }
});

/**
 * Remove the peripheral from the peripherals list.
 * Helper for handleUpdatePeripheral.
 */
function reapPeripheral(id) {
  delete _peripherals[id];
  RobotPeripheralStore.emitChange();
}

/**
 * Handles receiving an UPDATE_PERIPHERAL action.
 */
function handleUpdatePeripheral(action) {
  // If this is an existing peripheral,
  // we need to cancel the previous reaper.
  let existingPeripheral = _peripherals[action.peripheral.id];
  if (existingPeripheral !== undefined) {
    let reaper = existingPeripheral.get('reaper');
    clearTimeout(reaper);
  }

  // Create a new peripheral object with the new data we've received.
  let peripheral = action.peripheral;
  // Set a reaper to remove the peripheral in 2 seconds, IF no new data
  // is received. If new data is received within 2 seconds, the reaper
  // will be canceled.
  peripheral.reaper = setTimeout(reapPeripheral, 2000, action.peripheral.id);
  _peripherals[action.peripheral.id] = Map(peripheral);
  RobotPeripheralStore.emitChange();
}

RobotPeripheralStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.type) {
    case ActionTypes.UPDATE_PERIPHERAL:
      handleUpdatePeripheral(action);
      break;
  }
});

export default RobotPeripheralStore;
