import AppDispatcher from '../dispatcher/AppDispatcher';
import {ActionTypes} from '../constants/Constants';
import Ansible from '../utils/Ansible'
import fs from 'fs'
import {bridgeAddress, stationNumber} from '../utils/StationConfig'

let blue = stationNumber < 2
var FieldActions = {
  updateTimer(msg) {
    var timeLeft = msg.total_stage_time - msg.stage_time_so_far
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_TIMER,
      timeLeft: timeLeft,
      stage: msg.stage_name,
      totalTime: msg.total_stage_time
    });
  },
  updateHeart(msg) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_HEART,
      state: msg.state
    });
  },
  updateMatch(msg) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_MATCH,
      matchNumber: msg.match_number,
      teamNames: msg.team_names,
      teamNumbers: msg.team_numbers
    });
  },
  updateScore(msg) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_SCORE,
      state: msg.state,
      match_number: msg.matchNumber,
      pearl: msg.pearl, 
      water_autonomous: msg.water_autonomous, 
      treasure_autonomous: msg.treasure_autonomous, 
      water_teleop: msg.water_teleop, 
      treasure_teleop: msg.treasure_teleop
    });
  },
  updateRobot(msg) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_ROBOT,
      autonomous: msg.autonomous,
      enabled: msg.enabled
    });
    Ansible.sendMessage('competition', {'competition': true});
    Ansible.sendMessage('game', {'autonomous': msg.autonomous, 'enabled': msg.enabled, 'blue': blue})
    if (msg.running) {
      Ansible.sendMessage('execute', {});
    } else {
      Ansible.sendMessage('stop', {});
    }
  },
  updateLighthouseTimer(msg) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_LIGHTHOUSETIMER,
      timeLeft: msg.time_left,
      enabled: msg.enabled,
      available: msg.available
    });
  }
};


export default FieldActions;
