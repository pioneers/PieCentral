/**
 * Defines the Help menu
 */

import RendererBridge from '../RendererBridge';

const HelpMenu = {
  label: 'Help',
  submenu: [
    {
      label: 'Interactive Tutorial',
      click() {
        RendererBridge.registeredWindow.webContents.send('start-interactive-tour');
      },
    },
  ],
};

export default HelpMenu;
