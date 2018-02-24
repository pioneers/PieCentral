/**
 * Defines the Help menu
 */
import RendererBridge from '../RendererBridge';
import showAPI from '../main-process';

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
