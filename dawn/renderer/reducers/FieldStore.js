import { ActionTypes } from '../constants/Constants';
import { stationNumber } from '../../main/ansible/LCM';

const initialFieldState = {
  rIsBlue: stationNumber < 2,
  rTeamNumber: 0,
  rTeamName: 'Unknown',
  rStationTag: (stationNumber < 2) ? `Blue ${stationNumber + 1} ` : `Gold ${stationNumber - 1} `,
  heart: false,
  mMatchNumber: 0,
  mTeamNumbers: [0, 0, 0, 0],
  mTeamNames: ['Offline', 'Offline', 'Offline', 'Offline'],
};

const fieldStore = (state = initialFieldState, action) => {
  switch (action.type) {
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
        rTeamNumber: action.teamNumbers[stationNumber],
        rTeamName: action.teamNames[stationNumber],
      };
    default:
      return state;
  }
};

export default fieldStore;
