/**
 * RendererBridge connects the main process to the renderer's Redux flow.
 * Maintains a real-time copy of the renderer's Redux state in the main process, and
 * allows the main process to dispatch redux actions to the renderer.
 */

import _ from 'lodash';

const RendererBridge = {
  registeredWindow: null,

  registerWindow(electronWindow) {
    this.registeredWindow = electronWindow;
  },

  reduxDispatch(action) {
    if (this.registeredWindow) {
      this.registeredWindow.webContents.send('dispatch', action);
    }
  },
};

_.bindAll(RendererBridge, ['registerWindow', 'reduxDispatch']);

export default RendererBridge;
