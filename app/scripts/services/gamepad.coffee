'use strict'

angular.module('daemon.gamepad', ['daemon.radio'])

.service('gamepad', [
  '$interval'
  'radio'

  ($interval, radio) ->
    _gamepads = [undefined, undefined, undefined, undefined]
    _listeners = []
    _currTimestamp = [0, 0, 0, 0]

    updateGamepads = ->
      _gamepads = navigator.webkitGetGamepads()
      for g,index in _gamepads
        if g?
          _currTimestamp[index] = g.timestamp


    sendGamepads = ->
      updateGamepads()
      for listener in _listeners
        listener()
      if radio.initialized()
        for g,index in _gamepads
          if g? and _currTimestamp[index] != g.timestamp 
            radio.send(g.index, {buttons: g.buttons, axes: g.axes})
            _currTimestamp[index] = g.timestamp
              

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
        gamepadCount()
      validGamepads: ->
        validGamepads()
      registerListener: (func) ->
        _listeners.push(func)
    }
  ])