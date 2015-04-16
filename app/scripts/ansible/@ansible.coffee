# This file is capitalized so that it will be loaded before all other files
# with the same module.
angular.module('ansible', [])

.service 'ansible', ->

  HOSTNAME = 'localhost'
  PORT = 12345
  socket = io("http://#{HOSTNAME}:#{PORT}")

  return socket
