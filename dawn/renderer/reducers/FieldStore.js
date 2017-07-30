import { ActionTypes } from '../constants/Constants';

const initialFieldState = {
  stationNumber: 4,
  bridgeAddress: 'localhost',
  fieldControl: false,
  rTeamNumber: 0,
  rTeamName: 'Unknown',
  heart: false,
  mMatchNumber: 0,
  mTeamNumbers: [0, 0, 0, 0],
  mTeamNames: ['Offline', 'Offline', 'Offline', 'Offline'],
};

const fieldStore = (state = initialFieldState, action) => {
  switch (action.type) {
    case ActionTypes.UPDATE_FC_CONFIG:
      return {
        ...state,
        stationNumber: action.stationNumber,
        bridgeAddress: action.bridgeAddress,
      };
    case ActionTypes.FIELD_CONTROL:
      return {
        ...state,
        fieldControl: action.fieldControl,
      };
    case ActionTypes.UPDATE_HEART:
      return {
        ...state,
        heart: action.state,
      };
    case ActionTypes.UPDATE_MATCH:
      return {
        ...state,
        mMatchNumber: action.matchNumber,
        mTeamNumbers: action.teamNumbers,
        mTeamNames: action.teamNames,
        rTeamNumber: action.teamNumbers[state.stationNumber],
        rTeamName: action.teamNames[state.stationNumber],
      };
    default:
      return state;
  }
};

export default fieldStore;
