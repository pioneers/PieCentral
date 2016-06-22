/**
 * Actions for the console state.
 */

export const showConsole = () => ({
  type: 'SHOW_CONSOLE',
});

export const hideConsole = () => ({
  type: 'HIDE_CONSOLE',
});

export const updateConsole = (value) => ({
  type: 'UPDATE_CONSOLE',
  consoleOutput: value,
});

export const clearConsole = () => ({
  type: 'CLEAR_CONSOLE',
});
