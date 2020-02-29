/*
 * Entrypoint for Dawn's main process
 */

import {
  app, BrowserWindow, Menu,
} from 'electron';
/* eslint import/no-extraneous-dependencies: ["error", {"peerDependencies": true}] */
import installExtension, { REACT_DEVELOPER_TOOLS, REDUX_DEVTOOLS } from 'electron-devtools-installer';
import path from 'path';

import RendererBridge from './RendererBridge';
import Template from './MenuTemplate/Template';
import Client from './client';


app.on('window-all-closed', () => {
  app.quit();
});

app.on('will-quit', () => {
  Client.unbindIPCHandlers();
  Client.disconnect();
});

app.on('ready', () => {
  const mainWindow = new BrowserWindow({
    webPreferences: {
      nodeIntegration: true,
    },
  });

  // Binding for the main process to inject into Redux workflow
  RendererBridge.registerWindow(mainWindow);

  Client.bindIPCHandlers();

  mainWindow.maximize();
  mainWindow.loadURL(`file://${path.resolve()}/static/index.html`);

  const menu = Menu.buildFromTemplate(Template);
  Menu.setApplicationMenu(menu);

  if (process.env.NODE_ENV !== 'production') {
    installExtension(REACT_DEVELOPER_TOOLS).then((name) => {
      console.log(`Added Extension:  ${name}`);
    }).catch((err) => {
      console.log('An error occurred: ', err);
    });

    installExtension(REDUX_DEVTOOLS).then((name) => {
      console.log(`Added Extension:  ${name}`);
    }).catch((err) => {
      console.log('An error occurred: ', err);
    });
  }
});
