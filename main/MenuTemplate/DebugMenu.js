/**
 * Defines the debug menu.
 */

import RendererBridge from '../RendererBridge';
import { fork } from 'child_process';

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
    {
      label: 'Toggle Runtime',
      child: null,
      click() {
        if (child) {
          child.kill();
          child = null;
        } else {
          // Fork FakeRuntime as a child process
          child = fork('./fake-runtime/FakeRuntime');
        }
      },
    },
  ],
};

// In development mode, allow reloading to see effects of code changes.
if (process.env.NODE_ENV === 'development') {
  DebugMenu.submenu.unshift({
    label: 'Reload',
    accelerator: 'CommandOrControl+R',
    click() {
      RendererBridge.registeredWindow.reload();
    },
  });
}

export default DebugMenu;
