import { ActionTypes } from '../constants/Constants';
// import Ansible from '../utils/Ansible';

export const updateTimer = msg => ({
  type: ActionTypes.UPDATE_TIMER,
  timeLeft: msg.total_stage_time - msg.stage_time_so_far,
  stage: msg.stage_name,
  totalTime: msg.total_stage_time,
});

export const updateHeart = msg => ({
  type: ActionTypes.UPDATE_HEART,
  state: msg.state,
});

export const updateMatch = msg => ({
  type: ActionTypes.UPDATE_MATCH,
  matchNumber: msg.match_number,
  teamNames: msg.team_names,
  teamNumbers: msg.team_numbers,
});

export const updateScore = msg => ({
  type: ActionTypes.UPDATE_SCORE,
  state: msg.state,
  match_number: msg.matchNumber,
  pearl: msg.pearl,
  water_autonomous: msg.water_autonomous,
  treasure_autonomous: msg.treasure_autonomous,
  water_teleop: msg.water_teleop,
  treasure_teleop: msg.treasure_teleop,
});

/* TODO
if (msg.running) {
  Ansible.sendMessage('execute', {});
} else {
  Ansible.sendMessage('stop', {});
}*/
export const updateRobot = msg => ({
  type: ActionTypes.UPDATE_ROBOT,
  autonomous: msg.autonomous,
  enabled: msg.enabled,
});

export const updateLighthouseTimer = msg => ({
  type: ActionTypes.UPDATE_LIGHTHOUSETIMER,
  timeLeft: msg.time_left,
  enabled: msg.enabled,
  available: msg.available,
});
