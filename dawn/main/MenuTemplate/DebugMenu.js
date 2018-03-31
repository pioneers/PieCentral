import { fork } from 'child_process';
import RendererBridge from '../RendererBridge';
import FCObject from '../networking/FieldControl';

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
      accelerator: 'CommandOrControl+alt+I',
    },
    {
      label: 'Restart Runtime',
      click() {
        RendererBridge.reduxDispatch({
          type: 'RESTART_RUNTIME',
        });
      },
    },
    {
      label: 'Restart FC',
      click() {
        FCObject.FCInternal.quit();
        FCObject.setup();
      },
    },
    {
      label: 'Toggle Console Autoscroll',
      click() {
        RendererBridge.reduxDispatch({
          type: 'TOGGLE_SCROLL',
        });
      },
    },

    {
      label: 'Reload',
      accelerator: 'CommandOrControl+R',
      click() {
        RendererBridge.registeredWindow.reload();
      },
    },

    {
      label: 'Full Stack Timestamp',
      click() {
        RendererBridge.reduxDispatch({
          type: 'TIMESTAMP_CHECK',
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
}

export default DebugMenu;
