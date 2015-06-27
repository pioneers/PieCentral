# This file defines constants for use in the application.

# keyMirror is a utility that makes sets all values to the keys.
# We use this so that we can detect typos as runtime errors.
keyMirror = require('keymirror')

# Export is a dictionary.
module.exports =
  VERSION: '0.4.0'
  ActionTypes: keyMirror
    UPDATE_GAMEPADS: null
