AppDispatcher = require('../dispatcher/AppDispatcher')
Constants = require('../constants/Constants')
ActionTypes = Constants.ActionTypes

# state variable for debouncing gamepad updates
_timestamp = 0
# Private function that checks for updated Gamepad State
_updateGamepadState = ->
  newGamepads = navigator.getGamepads()
  if newGamepads[0]? and newGamepads[0].timestamp > _timestamp
    _timestamp = newGamepads[0].timestamp
    GamepadActionCreators.updateGamepads(newGamepads)

module.exports = GamepadActionCreators =

  updateGamepads: (gamepads) ->
    AppDispatcher.dispatch
      type: ActionTypes.UPDATE_GAMEPADS
      gamepads: gamepads

  # Instructs the action creator to poll the
  # HTML5 Gamepad API every delay milliseconds,
  # And emit an UPDATE_GAMEPADS action in the event
  # Of an update
  setUpdateInterval: (delay) ->
    # remove the previous interval, if present
    if this._interval?
      clearInterval(this._interval)
      this._interval = undefined

    this._interval = setInterval(_updateGamepadState, delay)
