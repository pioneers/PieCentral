// Electron entrypoint
'use strict';
const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
const Menu = electron.Menu;
const storage = require('electron-json-storage');
const ipcMain = electron.ipcMain;

let template = [
  {
    label: 'Dawn',
    submenu: [
      {
        label: 'Reset user settings',
        click: function() {
          storage.clear();
        }
      },
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
  },
  {
    label: 'Developer',
    submenu: [
      {
        label: 'Runtime Configuration',
        click: function() {
          mainWindow.webContents.send('show-runtime-config');
        }
      }
    ]
  }
];

// Keep track of whether dawn is connected to robot or not.
let runtimeConnected = false;
ipcMain.on('runtime-connect', function(event, arg) {
  runtimeConnected = true;
});

ipcMain.on('runtime-disconnect', function(event, arg) {
  runtimeConnected = false;
});

let mainWindow;
app.on('window-all-closed', function() {
  app.quit();
});

app.on('ready', function() {

  mainWindow = new BrowserWindow();
  mainWindow.maximize();

  mainWindow.loadURL(`file://${__dirname}/static/index.html`);

  mainWindow.on('closed', function() {
    mainWindow = null;
  });

  // Add open devtools option to main menu.
  template[2].submenu.unshift({
    label: 'Toggle DevTools',
    click: function() {
      mainWindow.webContents.toggleDevTools();
    }
  });

  // In development mode, allow quick reloading to see effects of code changes.
  if (process.env.NODE_ENV === 'development') {
    template[2].submenu.unshift({
      label: 'Reload',
      accelerator: 'CommandOrControl+R',
      click: function() {
        mainWindow.reload();
      }
    });
  }

  let menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
});
