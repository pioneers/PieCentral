'use strict'

angular.module('daemon.gamepad', [])

.service('gamepads', [
  '$interval'

  ($interval) ->
    _gamepads = [undefined, undefined, undefined, undefined]
    _callbacks = []
    _currentTimestamps = [0, 0, 0, 0]

    socket = io.connect('http://localhost:3000')

    sendGamepadData = (data)->
      socket.emit('gamepad', {data: data})

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

      sendGamepadData(JSON.stringify(_gamepads))

    $interval(update, 100)

    return {
      active: ->
        _.filter(_gamepads, (g) -> g?)
      all: ->
        _gamepads
      onUpdate: (func) ->
        _callbacks.push(func)
    }
  ])
