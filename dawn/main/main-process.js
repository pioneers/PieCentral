/*
 * Entrypoint for Dawn's main process
 */

import {
  app, BrowserWindow, Menu, ipcMain,
} from 'electron';
/* eslint import/no-extraneous-dependencies: ["error", {"peerDependencies": true}] */
import installExtension, { REACT_DEVELOPER_TOOLS, REDUX_DEVTOOLS } from 'electron-devtools-installer';

import RendererBridge from './RendererBridge';
import Template from './MenuTemplate/Template';
import Ansible from './networking/Ansible';
import FCObject from './networking/FieldControl';


app.on('window-all-closed', () => {
  app.quit();
});

app.on('will-quit', () => {
  Ansible.close();
  if (FCObject.FCInternal !== null) {
    FCObject.FCInternal.quit();
  }
});

function initializeFC(event) { // eslint-disable-line no-unused-vars
  try {
    FCObject.setup();
  } catch (err) {
    console.log(err);
  }
}

function teardownFC(event) { // eslint-disable-line no-unused-vars
  if (FCObject.FCInternal !== null) {
    FCObject.FCInternal.quit();
  }
}

app.on('ready', () => {
  Ansible.setup();
  ipcMain.on('FC_CONFIG_CHANGE', FCObject.changeFCInfo);
  ipcMain.on('FC_INITIALIZE', initializeFC);
  ipcMain.on('FC_TEARDOWN', teardownFC);

  const mainWindow = new BrowserWindow({
    webPreferences: {
      nodeIntegration: true,
    },
  });

  // Binding for the main process to inject into Redux workflow
  RendererBridge.registerWindow(mainWindow);

  mainWindow.maximize();
  mainWindow.loadURL(`file://${__dirname}/../static/index.html`);

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
