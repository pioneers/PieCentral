/**
 * Actions for the console state.
 */

export const showConsole = () => {
  return {
    type: 'SHOW_CONSOLE'
  };
};

export const hideConsole = () => {
  return {
    type: 'HIDE_CONSOLE'
  };
};

export const updateConsole = (value) => {
  return {
    type: 'UPDATE_CONSOLE',
    consoleOutput: value
  };
};

export const clearConsole = () => {
  return {
    type: 'CLEAR_CONSOLE'
  };
};
