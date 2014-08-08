# nw.gui requires it to be named require
require = window.requireNode
if require?
  gui = require('nw.gui')
  win = gui.Window.get()
  menubar = new gui.Menu(type: 'menubar')

  onMac = process.platform == 'darwin'
  if onMac
    menubar.createMacBuiltin('Daemon')
  debugMenu = new gui.Menu()

  debugMenu.append new gui.MenuItem(
    label: 'Reload'
    click: -> win.reload()
    key: 'r'
    modifiers: if onMac then 'cmd' else 'ctrl'
    )

  debugMenu.append new gui.MenuItem(
    label: 'Reload and Clear Cache'
    click: -> win.reloadIgnoringCache()
    key: 'r'
    modifiers: if onMac then 'cmd-shift' else 'shift-ctrl'
    )

  debugMenu.append new gui.MenuItem(
    label: "Toggle Kiosk Mode"
    click: -> win.toggleKioskMode()
    key: 'f'
    modifiers: if onMac then 'cmd-shift' else 'shift-ctrl'
    )

  debugMenu.append new gui.MenuItem type: 'separator'

  debugMenu.append new gui.MenuItem(
    label: 'Developer Tools'
    click: -> win.showDevTools()
    key: 'i'
    modifiers: if onMac then 'cmd-alt' else 'shift-ctrl'
    )

  menubar.append new gui.MenuItem(
    label: 'Developer'
    submenu: debugMenu
    )
  win.menu = menubar

angular.module('menubar', [])

.service('Menubar', [
  ->
    return menubar
  ])

