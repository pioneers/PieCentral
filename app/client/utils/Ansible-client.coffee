io = require('socket.io-client')
HOSTNAME = 'localhost'
PORT = '3000'
socket = io('http://#{HOSTNAME}:#{PORT}')
module.exports = socket
