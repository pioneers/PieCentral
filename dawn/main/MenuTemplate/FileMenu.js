/**
 * Defines the File menu
 */

import RendererBridge from '../RendererBridge';
import {
  openFile,
  saveFile,
  createNewFile,
} from '../../renderer/actions/EditorActions';

const FileMenu = {
  label: 'File',
  submenu: [
    {
      label: 'New File',
      click() {
        RendererBridge.reduxDispatch(createNewFile());
      },
      accelerator: 'CommandOrControl+N',
    },
    {
      label: 'Open file',
      click() {
        RendererBridge.reduxDispatch(openFile());
      },
      accelerator: 'CommandOrControl+O',
    },
    {
      label: 'Save file',
      click() {
        RendererBridge.reduxDispatch(saveFile());
      },
      accelerator: 'CommandOrControl+S',
    },
    {
      label: 'Save file as',
      click() {
        RendererBridge.reduxDispatch(saveFile(true));
      },
      accelerator: 'CommandOrControl+Shift+S',
    },
  ],
};

export default FileMenu;
