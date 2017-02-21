/**
 * Entrypoint for main process of Dawn.
 */

import { app, BrowserWindow, Menu } from 'electron';
import RendererBridge from './RendererBridge';
import Template from './MenuTemplate/Template';
import './ansible/Ansible';

let mainWindow; // the window which displays Dawn

app.on('window-all-closed', () => {
  app.quit();
});

app.on('ready', () => {
  mainWindow = new BrowserWindow();

  // connects to window's redux state and dispatcher
  RendererBridge.registerWindow(mainWindow);

  mainWindow.maximize();
  mainWindow.loadURL(`file://${__dirname}/../static/index.html`);

  mainWindow.on('closed', () => {
    if (process.env.NODE_ENV === 'development') {
      console.log(Template[3].submenu[1].kill()); // Find Less Hacky way to kill Fake Runtimes.
    }
    mainWindow = null;
  });

  const menu = Menu.buildFromTemplate(Template);
  Menu.setApplicationMenu(menu);
});
