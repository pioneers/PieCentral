/**
 * Connect the redux store to the main Electron process,
 * and listen to redux action dispatches from the main process.
 * Used for things like the File menu in the taskbar, which
 * needs to dispatch actions which affect the Editor state.
 */

import { ipcRenderer } from 'electron';
import { store } from '../configureStore';

ipcRenderer.on('dispatch', (event, action) => {
  store.dispatch(action);
});

store.subscribe(() => {
  ipcRenderer.send('stateUpdate', store.getState());
});
