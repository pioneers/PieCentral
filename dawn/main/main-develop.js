/*
 * Entrypoint for Dawn's main process
 */

import { app, BrowserWindow, Menu } from 'electron';
import RendererBridge from './RendererBridge';
import { killFakeRuntime } from './MenuTemplate/DebugMenu';
import Template from './MenuTemplate/Template';
import Ansible from './ansible/Ansible';

app.on('window-all-closed', () => {
  app.quit();
});

app.on('will-quit', () => {
  Ansible.close();

  if (process.env.NODE_ENV === 'development') {
    killFakeRuntime();
  }
});

app.on('ready', () => {
  Ansible.setup();

  const mainWindow = new BrowserWindow();

  // Binding for the main process to inject into Redux workflow
  RendererBridge.registerWindow(mainWindow);

  mainWindow.maximize();
  mainWindow.loadURL(`file://${__dirname}/../static/index.html`);

  const menu = Menu.buildFromTemplate(Template);
  Menu.setApplicationMenu(menu);
});
