'use strict'

angular.module('daemon.gamepad', ['daemon.radio'])

.service('gamepad', [
  '$interval'
  'radio'

  ($interval, radio) ->
    _gamepads = []
    _listeners = []

    updateGamepads = ->
      _gamepads = navigator.webkitGetGamepads()
      gamepad = _gamepads[0]
      if gamepad.timestamp != _timeStamp
        for fn in _updatefunctions
          fn(gamepad)

      _timeStamp = gamepad.timestamp

    sendGamepads = ->
      updateGamepads()
      for listener in _listeners
        listener()
      if radio._init
        for g in _gamepads
          radio.send(g.index, {buttons: g.buttons, axes: g.axes})

    gamepadCount = ->
      count = 0
      for g in _gamepads
        if g?
          count++
      return count

    validGamepads = ->
      updateGamepads()
      valid = []
      for g in _gamepads
        if g?
          valid.push(g)
      return valid

    $interval(sendGamepads, 100)

    return {
      updateGamepads: -> updateGamepads()
      gamepadCount: ->
        gamepadCounter()
      validGamepads: ->
        validGamepads()
      registerListener: (func) ->
        _listeners.push(func)
    }
  ])