# nw.gui requires it to be named require
require = window.requireNode
gui = require('nw.gui')
win = gui.Window.get()
menubar = new gui.Menu(type: 'menubar')
menubar.createMacBuiltin('Daemon')
debugMenu = new gui.Menu()

debugMenu.append new gui.MenuItem(
  label: "Reload"
  click: -> win.reload()
  key: "r"
  modifiers: "cmd"
  )

debugMenu.append new gui.MenuItem(
  label: "Reload and Clear Cache"
  click: -> win.reloadIgnoringCache()
  key: "r"
  modifiers: "cmd-shift"
  )

debugMenu.append new gui.MenuItem(
  label: "Toggle Kiosk Mode"
  click: -> win.toggleKioskMode()
  key: "f"
  modifiers: "cmd-shift"
  )

debugMenu.append new gui.MenuItem type: 'separator'

debugMenu.append new gui.MenuItem(
  label: "Developer Tools"
  click: -> win.showDevTools()
  key: "i"
  modifiers: "cmd-alt"
  )

menubar.append new gui.MenuItem(
  label: 'Developer'
  submenu: debugMenu
  )
win.menu = menubar
