import { ActionTypes } from '../constants/Constants';

const initialTimerState = {
  timestamp: 0,
  timeLeft: 0,
  computedTime: 0, // TODO: Questionable if this should even be in the store
  totalTime: 0,

};

const TimerStore = (state = initialTimerState, action) => {
  switch (action.type) {
    case ActionTypes.UPDATE_TIMER:
      return {
        ...state,
        timestamp: Date.now(),
        timeLeft: action.timeLeft,
        computedTime: action.timeLeft,
        stage: action.stage,
        totalTime: action.totalTime,
      };
    default:
      return state;
  }
};
// TODO: Move Elsewhere
// function refreshTimer() {
//   let timeLeft = (_timerData.timeLeft - (Date.now() - _timerData.timestamp));
//   if (timeLeft < 0){
//     timeLeft = 0;
//   }
//   _timerData.computedTime = timeLeft;
// }
// setInterval(refreshTimer, 200);

export default TimerStore;
