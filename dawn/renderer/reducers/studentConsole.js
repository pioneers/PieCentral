/**
 * Reducer for console state data
 */

const initialState = {
  showConsole: false,
  consoleData: [],
};

const studentConsole = (state = initialState, action) => {
  switch (action.type) {
    case 'UPDATE_CONSOLE':
      return {
        ...state,
        consoleData: [
          ...state.consoleData,
          action.consoleOutput,
        ],
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
      };
    default:
      return state;
  }
};

export default studentConsole;
