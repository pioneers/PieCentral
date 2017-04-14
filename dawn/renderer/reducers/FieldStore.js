import { ActionTypes } from '../constants/Constants';
import { stationNumber } from '../utils/LCM';

const initialFieldState = {
  rStation: stationNumber,
  rIsBlue: stationNumber < 2,
  rTeamNumber: 0,
  rTeamName: 'Unknown',
  rStationTag: (stationNumber < 2) ? `Blue ${stationNumber + 1} ` : `Gold ${stationNumber - 1} `,
  heart: false,
  sBlue: 0,
  sGold: 1,
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
        rTeamNumber: action.teamNumbers[state.rStation],
        rTeamName: action.teamNames[state.rStation],
      };
    case ActionTypes.UPDATE_SCORE:
      return {
        ...state,
        sBlue: (20 * action.treasure_autonomous[0])
        + (15 * action.treasure_autonomous[1])
        + (10 * action.treasure_teleop[0])
        + (5 * action.treasure_teleop[1]),
        sGold: (20 * action.treasure_autonomous[2])
        + (15 * action.treasure_autonomous[3])
        + (10 * action.treasure_teleop[2])
        + (5 * action.treasure_teleop[3]),
      };
    default:
      return state;
  }
};

export default fieldStore;
