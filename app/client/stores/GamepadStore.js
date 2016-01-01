import AppDispatcher from '../dispatcher/AppDispatcher';
import { EventEmitter } from 'events';
import assign from 'object-assign';
import { ActionTypes } from '../constants/Constants';
import GamepadActionCreators from '../actions/GamepadActionCreators';

var gamepads = undefined;

var GamepadStore = assign({}, EventEmitter.prototype, {
  emitChange() {
    this.emit('change');
  },
  getGamepads() {
    return gamepads;
  }
});

var handleGamepadUpdates = function(action) {
  gamepads = action.gamepads;
  GamepadStore.emitChange();
};

GamepadStore.dispatchToken = AppDispatcher.register((action)=>{
  switch (action.type) {
    case ActionTypes.UPDATE_GAMEPADS:
      handleGamepadUpdates(action);
      break;
  }
});

GamepadActionCreators.setUpdateInterval(50);

export default GamepadStore;
