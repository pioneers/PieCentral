/*
 * Entrypoint for Dawn's main process
 */

import { app, BrowserWindow, Menu } from 'electron';
import RendererBridge from './RendererBridge';
import Template from './MenuTemplate/Template';
import './ansible/Ansible'; // Ansible is initiated here

let mainWindow;

app.on('window-all-closed', () => {
  app.quit();
});

app.on('ready', () => {
  mainWindow = new BrowserWindow();

  // Binding for the main process to inject into Redux workflow
  RendererBridge.registerWindow(mainWindow);

  mainWindow.maximize();
  mainWindow.loadURL(`file://${__dirname}/../static/index.html`);

  mainWindow.on('closed', () => {
    if (process.env.NODE_ENV === 'development') {
      // TODO: Find less odd way to prevent hanging Fake Runtimes
      console.log(Template[3].submenu[1].kill());
    }
    mainWindow = null;
  });

  const menu = Menu.buildFromTemplate(Template);
  Menu.setApplicationMenu(menu);
});
