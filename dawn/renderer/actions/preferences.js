import { createActions, handleActions } from 'redux-actions';

export const { toggleDarkTheme } = createActions({
  TOGGLE_DARK_THEME: () => null,
});
