# nw.gui requires it to be named require
# huge hack, needs to be kept outside of Angular
require = window.requireNode

angular.module('daemon.menubar', ['daemon.fieldcontrol'])

.service('menubar', [
  'fieldcontrol'
  (fieldcontrol) ->
    gui = require('nw.gui')
    win = gui.Window.get()
    menubar = new gui.Menu(type: 'menubar')

    onMac = process.platform == 'darwin'
    if onMac
      menubar.createMacBuiltin('Daemon')

    fieldControlMenu = new gui.Menu()

    fieldControlMenu.append new gui.MenuItem
      label: 'Teleop'
      # click: -> radio.setTeleoperated()
      key: '1'
      modifiers: if onMac then 'cmd-shift' else 'ctrl-shift'

    fieldControlMenu.append new gui.MenuItem
      label: 'Autonomous'
      # click: -> radio.setAutonomous()
      key: '2'
      modifiers: if onMac then 'cmd-shift' else 'ctrl-shift'

    fieldControlMenu.append new gui.MenuItem
      label: 'Emergency Stop'
      # click: -> radio.emergencyStop()
      key: 'e'
      modifiers: if onMac then 'cmd' else 'ctrl'

    fieldControlMenu.append new gui.MenuItem type: 'separator'

    fieldControlMenu.append new gui.MenuItem
      type: 'checkbox'
      label: 'Listen to Field Control'
      click: ->
        if this.checked
          fieldcontrol.init('ws://10.31.3.1:8000')
        else
          fieldcontrol.close()
      checked: false

    menubar.append new gui.MenuItem
      label: 'Robot Control'
      submenu: fieldControlMenu

    debugMenu = new gui.Menu()

    debugMenu.append new gui.MenuItem
      label: 'Reload'
      click: -> win.reload()
      key: 'r'
      modifiers: if onMac then 'cmd' else 'ctrl'

    debugMenu.append new gui.MenuItem
      label: 'Reload and Clear Cache'
      click: -> win.reloadIgnoringCache()
      key: 'r'
      modifiers: if onMac then 'cmd-shift' else 'shift-ctrl'

    debugMenu.append new gui.MenuItem
      label: "Toggle Kiosk Mode"
      click: -> win.toggleKioskMode()
      key: 'f'
      modifiers: if onMac then 'cmd-shift' else 'shift-ctrl'

    debugMenu.append new gui.MenuItem type: 'separator'

    debugMenu.append new gui.MenuItem
      label: 'Developer Tools'
      click: -> win.showDevTools()
      key: 'i'
      modifiers: if onMac then 'cmd-alt' else 'shift-ctrl'

    menubar.append new gui.MenuItem
      label: 'Developer'
      submenu: debugMenu

    win.menu = menubar
    return menubar
])
.run(['menubar', (menubar) -> console.log 'bootstrapping menu bar...'])

