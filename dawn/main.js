// Electron entrypoint
'use strict';
const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
const Menu = electron.Menu;

let template = [
  {
    label: 'Dawn',
    submenu: [
      {
        label: 'Quit',
        accelerator: 'CommandOrControl+Q',
        click: function() { app.quit(); }
      }
    ]
  },
  {
    label: 'Edit',
    submenu: [
      {
        label: 'Cut',
        accelerator: 'CommandOrControl+X',
        role: 'cut'
      },
      {
        label: 'Copy',
        accelerator: 'CommandOrControl+C',
        role: 'copy'
      },
      {
        label: 'Paste',
        accelerator: 'CommandOrControl+V',
        role: 'paste'
      }
    ]
  }
];

let mainWindow;
app.on('window-all-closed', function() {
  if (process.platform != 'darwin') {
    app.quit();
  }
});

app.on('ready', function() {

  mainWindow = new BrowserWindow();
  mainWindow.maximize();

  mainWindow.loadURL('file://' + __dirname + '/static/index.html');
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools(); // Open dev tools
  }
  mainWindow.on('closed', function() {
    mainWindow = null;
  });

  let menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
});
