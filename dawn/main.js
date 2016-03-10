// Electron entrypoint
'use strict';
const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
const Menu = electron.Menu;
const request = require('superagent');
const storage = require('electron-json-storage');

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
  },
  {
    label: 'Developer',
    submenu: [
      {
        label: 'Restart Runtime',
        click: function() {
          storage.has('runtimeAddress', (err, hasKey)=>{
            if(hasKey) {
              storage.get('runtimeAddress', (err, data)=>{
                let runtimeAddress = data.address;
                request.get(
                  `http://${runtimeAddress}:5000/restart`).end((err, res)=>{
                    if (err) {
                      console.log('Error on restart:', err);
                    }
                  }
                );
              });
            }
          });
        }
      }
    ]
  }
];

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
