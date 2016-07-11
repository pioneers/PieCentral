/**
 * Defines the Dawn menu
 */

import { app } from 'electron';

const DawnMenu = {
  label: 'Dawn',
  submenu: [
    {
      label: 'Quit',
      accelerator: 'CommandOrControl+Q',
      click() {
        app.quit();
      },
    },
  ],
};

export default DawnMenu;
