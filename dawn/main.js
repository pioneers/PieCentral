// Electron entrypoint
'use strict';
const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;

let mainWindow;

app.on('window-all-closed', function() {
  if (process.platform != 'darwin') {
    app.quit();
  }
});

app.on('ready', function() {

  electronScreen = electron.screen;
  size = electronScreen.getPrimaryDisplay().workAreaSize;
  mainWindow = new BrowserWindow({width: size.width, height: size.height});

  mainWindow.loadURL('file://' + __dirname + '/static/index.html');

  mainWindow.webContents.openDevTools(); // Open dev tools

  mainWindow.on('closed', function() {
    mainWindow = null;
  });
});
