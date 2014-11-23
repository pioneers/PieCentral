'use strict'

angular.module('daemon.gamepad', ['daemon.radio'])

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
          if radio.initialized()
            radio.send('gp' + String(gamepad.index),
              {axes: gamepad.axes})
          # update the timestamps
          _currentTimestamps[i] = gamepad.timestamp

    $interval(update, 100)

    return {
      active: ->
        _.filter(_gamepads, (g) -> g?)
      all: ->
        _gamepads
      count: ->
        _.filter(_gamepads, (g) -> g?).length
      onUpdate: (func) ->
        _callbacks.push(func)
    }
  ])