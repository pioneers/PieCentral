import { fork } from 'child_process';
import RendererBridge from '../RendererBridge';

let fakeRuntime = null;

export function killFakeRuntime() {
  if (fakeRuntime) {
    fakeRuntime.kill();
    fakeRuntime = null;
    console.log('Fake runtime killed');
  }
}

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
    click() {
      if (fakeRuntime) {
        killFakeRuntime();
      } else {
        fakeRuntime = fork('./fake-runtime/FakeRuntime');
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
