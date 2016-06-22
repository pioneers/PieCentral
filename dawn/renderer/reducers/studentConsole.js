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
          action.console_output.value,
        ],
      };
    case 'CLEAR_CONSOLE':
      return {
        ...state,
        consoleData: [],
      };
    case 'SHOW_CONSOLE':
      return {
        ...state,
        showConsole: true,
      };
    case 'HIDE_CONSOLE':
      return {
        ...state,
        showConsole: false,
      };
    default:
      return state;
  }
};

export default studentConsole;
