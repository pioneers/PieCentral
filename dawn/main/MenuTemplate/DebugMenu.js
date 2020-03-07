import RendererBridge from '../RendererBridge';
import FCObject from '../networking/FieldControl';

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

export default DebugMenu;
