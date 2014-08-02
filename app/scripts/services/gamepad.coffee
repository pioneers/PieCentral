'use strict'

angular.module('daemon.gamepad', [])

.service('gamepads', [
  '$interval'
  ($interval) ->
    _gamepads = undefined

    updateGamepads = ->
      _gamepads = navigator.webkitGetGamepads()

    $interval(updateGamepads, 50)

    return {
      gamepad: -> 
        _gamepads[0]
      gamepads: ->
        _gamepads
    }
  ])