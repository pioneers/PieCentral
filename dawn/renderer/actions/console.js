import { createActions, handleActions } from 'redux-actions';

export const { append, open, close, clear, copy } = createActions({
  APPEND: (line) => ({ line }),
  OPEN: () => ({ isOpen: true }),
  CLOSE: () => ({ isOpen: false }),
  CLEAR: () => null,
});
