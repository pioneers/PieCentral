import { ActionTypes } from '../constants/Constants';

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

export const updateRobot = msg => ({
  type: ActionTypes.UPDATE_ROBOT,
  autonomous: msg.autonomous,
  enabled: msg.enabled,
});

export const toggleFieldControl = msg => ({
  type: ActionTypes.FIELD_CONTROL,
  fieldControl: msg,
});

export const updateFieldControl = msg => ({
  type: ActionTypes.UPDATE_FC_CONFIG,
  stationNumber: msg.stationNumber,
  bridgeAddress: msg.bridgeAddress,
});
