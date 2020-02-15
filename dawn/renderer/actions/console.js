import { createActions, handleActions } from 'redux-actions';

export const { append, toggle, clear, copy } = createActions({
  APPEND: (record) => record,
  TOGGLE: () => null,
  CLEAR: () => null,
});
