# This file is capitalized so that it will be loaded before all other files
# with the same module.
angular.module('ansible', [])

.service 'ansible', ->

  HOSTNAME = 'localhost'
  PORT = 12345
  socket = io("http://#{HOSTNAME}:#{PORT}")

  return socket

# reports over ansible the status of the gamepads
.service 'gamepadReporter', [
  '$interval'
  'ansible'
  ($interval, ansible) ->
    update = ->
      gamepads = navigator.getGamepads()
      ansible.send(gamepads)

    $interval(update, 100)
  ]
