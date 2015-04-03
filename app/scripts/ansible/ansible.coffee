angular.module('ansible', [])

.service 'ansible', ->

  HOSTNAME = 'localhost'
  PORT = 12345
  socket = io("http://#{HOSTNAME}:#{PORT}")

  return socket
