/**
 * Reducer for console state data
 */

const initialState = {
  showConsole: false,
  consoleData: [],
  disableScroll: false,
  consoleUnread: false,
};

const MAX_LINES = 512;

const studentConsole = (state = initialState, action) => {
  switch (action.type) {
    case 'UPDATE_CONSOLE':
      return {
        ...state,
        consoleData: [
          ...state.consoleData,
          action.consoleOutput,
        ].slice(-MAX_LINES),
        consoleUnread: !state.showConsole,
      };
    case 'CLEAR_CONSOLE':
      return {
        ...state,
        consoleData: [],
      };
    case 'TOGGLE_CONSOLE':
      return {
        ...state,
        showConsole: !state.showConsole,
        consoleUnread: false,
      };
    case 'TOGGLE_SCROLL':
      return {
        ...state,
        disableScroll: !state.disableScroll,
      };
    default:
      return state;
  }
};

export default studentConsole;
