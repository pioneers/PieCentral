import AppDispatcher from '../dispatcher/AppDispatcher';
import { ActionTypes } from '../constants/Constants';
import Ansible from '../utils/Ansible';
import _ from 'lodash';

var _timestamps = [0, 0, 0, 0];

var _needToUpdate = function(newGamepads) {
  return _.some(newGamepads, function(gamepad, index) {
    if(!_.isUndefined(gamepad) && (gamepad.timestamp > _timestamps[index])) {
      _timestamps[index] = gamepad.timestamp;
      return true;
    } else if (_.isUndefined(gamepad) && !_.isNull(_timestamps[index])) {
      _timestamps[index] = null;
      return true;
    }
    return false;
  });
};

var _formatGamepadsForJSON = function(newGamepads) {
  let formattedGamepads = {};
  // Currently there is a bug on windows where navigator.getGamepads()
  // returns a second, 'ghost' gamepad even when only one is connected.
  // The filter on 'mapping' filters out the ghost gamepad.
  _.forEach(_.filter(newGamepads, {'mapping': 'standard'}), function(gamepad) {
    if (gamepad) {
      formattedGamepads[gamepad.index] = {
        index: gamepad.index,
        axes: gamepad.axes,
        buttons: _.map(gamepad.buttons, 'value')
      };
    }
  });
  return formattedGamepads;
};

// Private function that checks for updated Gamepad State
// Also sends data to griff by emitting to socket-bridge
var _updateGamepadState = function() {
  let newGamepads = navigator.getGamepads();
  if (_needToUpdate(newGamepads)) {
    if (_.some(newGamepads)) {
      Ansible.sendMessage('gamepad', _formatGamepadsForJSON(newGamepads));
    }
    GamepadActionCreators.updateGamepads(newGamepads);
  }
};

var GamepadActionCreators = {
  updateGamepads(gamepads) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_GAMEPADS,
      gamepads: gamepads
    });
  },
  setUpdateInterval(delay) {
    // remove the previous interval, if present
    if(this._interval !== undefined) {
      clearInterval(this._interval);
      this._interval = undefined;
    }
    this._interval = setInterval(_updateGamepadState, delay);
  }
};

export default GamepadActionCreators;
