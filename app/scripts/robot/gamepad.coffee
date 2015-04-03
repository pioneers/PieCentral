'use strict'

angular.module('daemon.gamepad', ['ansible'])

.service('gamepadReporter', [
  '$interval'
  'ansible'
  ($interval, ansible) ->
    update = ->
      gamepads = navigator.getGamepads()
      ansible.send(gamepads)

    $interval(update, 100)
  ])
