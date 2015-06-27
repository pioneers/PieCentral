AppDispatcher = require('../dispatcher/AppDispatcher')
Constants = require('../constants/Constants')
EventEmitter = require('events').EventEmitter
assign = require('object-assign')
Environment = require('../utils/Environment')
ActionTypes = Constants.ActionTypes

# A singleton variable representing the current gamepad state.
gamepads = undefined

GamepadStore = assign({}, EventEmitter.prototype, {
  # shorthand for emitting change
  emitChange: -> this.emit('change')

  # public accessor method for the gamepads
  getGamepads: -> gamepads
})

# Here, we register our Store's listening callback
# The dispatchToken is so the Flux dispatcher can coordinate waiting.
GamepadStore.dispatchToken = AppDispatcher.register (action) ->
  # We inspect the action.type. If it's the type we need,
  # We act on it. (We discard all others)
  switch action.type
    when ActionTypes.UPDATE_GAMEPADS
      gamepads = action.gamepads
      GamepadStore.emitChange() # tell all views that state has changed

### Non-Flux part
This is the part of the program that isn't very Flux like.
It's necessary because in a normal Flux program, all actions are result of interaction
With React components (with actions triggered in components)
Or as the result of asynchronous calls that were initially triggered by calling
Action Creators (and handled inside)
###
if Environment.isBrowser # check if we're running in the browser
  GamepadActionCreators = require('../actions/GamepadActionCreators')
  GamepadActionCreators.setUpdateInterval(7) # poll every 7 ms (~140Hz)
### End Non-Flux part ###

module.exports = GamepadStore
