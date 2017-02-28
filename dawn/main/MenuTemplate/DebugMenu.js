/**
 * Defines the debug menu.
 */

import { fork } from 'child_process';
import RendererBridge from '../RendererBridge';

// Reference to the child process for FakeRuntime.
let child = null;

const DebugMenu = {
  label: 'Debug',
  submenu: [
    {
      label: 'Toggle DevTools',
      click() {
        RendererBridge.registeredWindow.webContents.toggleDevTools();
      },
    },
  ],
};

// In development mode, allow reloading to see effects of code changes.
if (process.env.NODE_ENV === 'development') {
  DebugMenu.submenu.unshift({
    label: 'Toggle Fake Runtime',
    kill() {
      if (child) {
        child.kill();
        child = null;
      }
      return 'Done';
    },
    click() {
      if (child) {
        child.kill();
        child = null;
      } else {
        // Fork FakeRuntime as a child process
        child = fork('./fake-runtime/FakeRuntime');
      }
    },
  });
  DebugMenu.submenu.unshift({
    label: 'Reload',
    accelerator: 'CommandOrControl+R',
    click() {
      RendererBridge.registeredWindow.reload();
    },
  });
}

export default DebugMenu;
