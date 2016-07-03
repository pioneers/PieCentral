/**
 * Entrypoint for main process of Dawn.
 */

import { app, BrowserWindow, Menu } from 'electron';
import storage from 'electron-json-storage';
import {
  openFile,
  saveFile,
  createNewFile,
} from '../renderer/actions/EditorActions';
import RendererBridge from './RendererBridge';
import FakeRuntime from './FakeRuntime';

let mainWindow; // the window which displays Dawn
const template = [
  {
    label: 'Dawn',
    submenu: [
      {
        label: 'Reset user settings',
        click() {
          storage.clear();
        },
      },
      {
        label: 'Quit',
        accelerator: 'CommandOrControl+Q',
        click() {
          app.quit();
        },
      },
    ],
  },
  {
    label: 'File',
    submenu: [
      {
        label: 'New File',
        click() {
          RendererBridge.reduxDispatch(createNewFile());
        },
      },
      {
        label: 'Open file',
        click() {
          RendererBridge.reduxDispatch(openFile());
        },
      },
      {
        label: 'Save file',
        click() {
          const filepath = RendererBridge.reduxState.editor.filepath;
          const code = RendererBridge.reduxState.editor.editorCode;
          RendererBridge.reduxDispatch(saveFile(filepath, code));
        },
      },
      {
        label: 'Save file as',
        click() {
          RendererBridge.reduxDispatch(saveFile(null, RendererBridge.reduxState.editor.editorCode));
        },
      },
    ],
  },
  {
    label: 'Edit',
    submenu: [
      {
        label: 'Cut',
        accelerator: 'CommandOrControl+X',
        role: 'cut',
      },
      {
        label: 'Copy',
        accelerator: 'CommandOrControl+C',
        role: 'copy',
      },
      {
        label: 'Paste',
        accelerator: 'CommandOrControl+V',
        role: 'paste',
      },
    ],
  },
  {
    label: 'Debug',
    submenu: [
      {
        label: 'Simulate Competition',
        click() {
          mainWindow.webContents.send('simulate-competition');
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
  },
  {
    label: 'Config',
    submenu: [
      {
        label: 'Runtime Config',
        click() {
          mainWindow.webContents.send('show-runtime-config');
        },
      },
    ],
  },
  {
    label: 'Help',
    submenu: [
      {
        label: 'Interactive Tutorial',
        click() {
          mainWindow.webContents.send('start-interactive-tour');
        },
      },
    ],
  },
];

app.on('window-all-closed', () => {
  app.quit();
});

app.on('ready', () => {
  mainWindow = new BrowserWindow();

  // connects to window's redux state and dispatcher
  RendererBridge.registerWindow(mainWindow);

  mainWindow.maximize();
  mainWindow.loadURL(`file://${__dirname}/static/index.html`);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Add open devtools option to main menu.
  template[3].submenu.unshift({
    label: 'Toggle DevTools',
    click() {
      mainWindow.webContents.toggleDevTools();
    },
  });

  // In development mode, allow quick reloading to see effects of code changes.
  if (process.env.NODE_ENV === 'development') {
    template[3].submenu.unshift({
      label: 'Reload',
      accelerator: 'CommandOrControl+R',
      click() {
        mainWindow.reload();
      },
    });
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
});
