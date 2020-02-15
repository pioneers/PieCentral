import { createActions, handleActions } from 'redux-actions';

export const { append, toggle, clear, copy } = createActions({
  APPEND: (line) => ({ line }),
  TOGGLE: () => null,
  CLEAR: () => null,
});
