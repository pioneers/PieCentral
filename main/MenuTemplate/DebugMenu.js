/**
 * Defines the debug menu.
 */

import RendererBridge from '../RendererBridge';
import FakeRuntime from '../FakeRuntime';

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
      click() {
        if (FakeRuntime.isActive()) {
          FakeRuntime.stop();
        } else {
          FakeRuntime.start(500);
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
