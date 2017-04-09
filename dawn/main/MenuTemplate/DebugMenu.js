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
    {
      label: 'Restart Runtime',
      click() {
        RendererBridge.reduxDispatch({
          type: 'RESTART_RUNTIME',
        });
      },
    },
  ],
};

if (process.env.NODE_ENV === 'development') {
  DebugMenu.submenu.push({
    label: 'Toggle Fake Runtime',
    click() {
      if (fakeRuntime) {
        killFakeRuntime();
      } else {
        fakeRuntime = fork('./fake-runtime/FakeRuntime');
      }
    },
  });

  DebugMenu.submenu.push({
    label: 'Reload',
    accelerator: 'CommandOrControl+R',
    click() {
      RendererBridge.registeredWindow.reload();
    },
  });
}

export default DebugMenu;
