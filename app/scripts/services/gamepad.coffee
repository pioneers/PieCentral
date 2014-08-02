'use strict'

angular.module('daemon.gamepad', [])

.service('gamepads', [
  '$interval'
  ($interval) ->
    _gamepads = undefined
    updateGamepads = ->
      _gamepads = navigator.webkitGetGamepads()

    gamepadCounter = ->
      count = 0
      for g in _gamepads 
        if g?
          count++
      return count
    
    validGamepads = ->
      valid = []
      for g in _gamepads
        if g?
          valid.push(g)
      return valid

    $interval(updateGamepads, 50)

    
    
    return {
      gamepadCounter: ->
        gamepadCounter()

      validGamepads: ->
        validGamepads()
    }
  ])