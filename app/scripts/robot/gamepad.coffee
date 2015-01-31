'use strict'

angular.module('daemon.gamepad', [])

.service('gamepads', [
  '$interval'
  'radio'

  ($interval, radio) ->
    _gamepads = [undefined, undefined, undefined, undefined]
    _callbacks = []
    _currentTimestamps = [0, 0, 0, 0]

    update = ->
      # call callbacks if we made change, but only once
      callCallbacksOnce = _.once( -> fn() for fn in _callbacks )

      # get the gamepads
      _gamepads = navigator.getGamepads()

      for i in [0...3]
        gamepad = _gamepads[i]
        oldTimestamp = _currentTimestamps[i]

        # if the gamepad isn't undefined
        if gamepad?
          callCallbacksOnce()
          # update the timestamps
          _currentTimestamps[i] = gamepad.timestamp

    $interval(update, 100)

    return {
      all: ->
        _gamepads
      onUpdate: (func) ->
        _callbacks.push(func)
    }
  ])