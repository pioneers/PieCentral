import { createActions, handleActions } from 'redux-actions';

export const MIN_LINES = 10;
export const MAX_LINES = 1000;

const clip = (lines) => Math.max(MIN_LINES, Math.min(MAX_LINES, lines));

export const { append, toggle, clear, copy, truncate } = createActions({
  APPEND: (record) => ({ record }),
  TOGGLE: () => null,
  CLEAR: () => null,
  TRUNCATE: (maxLines) => ({
    maxLines: isFinite(maxLines) ? clip(maxLines) : MIN_LINES
  }),
});
