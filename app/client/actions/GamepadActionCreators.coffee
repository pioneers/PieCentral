AppDispatcher = require('../dispatcher/AppDispatcher')
Constants = require('../constants/Constants')
ActionTypes = Constants.ActionTypes
AnsibleClient = require('../utils/AnsibleClient')

# state variable for debouncing gamepad updates
_timestamps = [0, 0, 0, 0]

_needToUpdate = (newGamepads) ->
  for gamepad, index in newGamepads
    if gamepad? and gamepad.timestamp > _timestamps[index]
      _timestamps[index] = gamepad.timestamp
      return true # this short circuits even though there
      # might be multiple updates in the same tick.
      # I'm doing this intentionally to reduce complexity.
  return false

_formatGamepadsForJSON = (newGamepads) ->
  formattedGamepads = {}
  for gamepad in newGamepads
    if gamepad?
      formattedGamepads[gamepad.index] =
        index: gamepad.index
        axes: gamepad.axes
  return formattedGamepads

# Private function that checks for updated Gamepad State
# Also sends data to griff by emitting to socket-bridge
_updateGamepadState = ->
  newGamepads = navigator.getGamepads()
  if _needToUpdate(newGamepads)
    AnsibleClient.sendMessage('gamepad', _formatGamepadsForJSON(newGamepads))
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
