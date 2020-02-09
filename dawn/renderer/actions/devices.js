import { createActions, handleActions } from 'redux-actions';

export const { addDevice, renameDevice } = createActions({
  ADD_DEVICE: () => ({}),
  RENAME_DEVICE: (index, alias) => ({ index, alias }),
});
