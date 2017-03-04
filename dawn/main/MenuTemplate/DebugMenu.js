import { fork } from 'child_process';
import RendererBridge from '../RendererBridge';

// Fake Runtime Instance
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

if (process.env.NODE_ENV === 'development') {
  DebugMenu.submenu.unshift({
    label: 'Toggle Fake Runtime',
    kill() { // Also called by main-develop.js
      if (child) {
        child.kill();
        child = null;
      }
      return 'Fake Runtime Killed';
    },
    click() {
      if (child) {
        child.kill();
      } else {
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
