/**
 * Defines the Help menu
 */
import BrowserWindow from 'electron';
import RendererBridge from '../RendererBridge';

function showAPI() {
  let api = new BrowserWindow({
    webPreferences: {
      nodeIntegration: false,
    },
    width: 1400,
    height: 900,
    show: false,
  });
  api.on('closed', () => {
    api = null;
  });
  api.loadURL(`file://${__dirname}/../static/website-robot-api-master/robot_api.html`);
  api.once('ready-to-show', () => {
    api.show();
  });
}

const HelpMenu = {
  label: 'Help',
  submenu: [
    {
      label: 'Interactive Tutorial',
      click() {
        RendererBridge.registeredWindow.webContents.send('start-interactive-tour');
      },
      accelerator: 'CommandOrControl+T',
    },
    {
      label: 'PiE API',
      click() {
        showAPI();
      },
      accelerator: 'CommandOrControl+P',
    },
  ],
};

export default HelpMenu;
