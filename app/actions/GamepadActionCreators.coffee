AppDispatcher = require('../dispatcher/AppDispatcher')
Constants = require('../constants/Constants')
ActionTypes = Constants.ActionTypes

module.exports =

  updateGamepads: (gamepads) ->
    AppDispatcher.dispatch
      type: ActionTypes.UPDATE_GAMEPADS
      gamepads: gamepads
